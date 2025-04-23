import datetime
import logging
import os
import signal
import time
from asyncio import create_task
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app_logger import logger
from clinicians import INITIAL_DATA, ClinicianStatus
from email_utils import send_alert
from models import ClinicianInfo
from utils import check_clinician_within_bounds, query_location

# Setting polling to 3 minutes since it gives us enough time to account
# for network errors, emailing errors, etc and to reach our SLA of 5 mins
# Worst case -> 7 users * 3 retries * 10 seconds ~= 2 minutes
# Accounting for ideal case -> 4 minutes
POLL_INTERVAL = 4 * 60
ERROR_POLL_INTERVAL = 10
ERROR_RETRY_LIMT = 3

# ENHANCEMENT: Use a database for this.
# Redis would be a good fit given the atomicity and consistency requirements
PHLEBOTOMIST_DATA = INITIAL_DATA


@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    FastAPI Server's lifespan function to run on setup and shutdown
    """
    create_task(poll_locations())
    yield
    os.kill(os.getpid(), signal.SIGTERM)


app = FastAPI(title="Phlebotomist Monitor", version="1.0.0", lifespan=lifespan)


def clinician_workflow(clinician: ClinicianInfo):
    """Query the location of a clinician and alert accordingly.

    Steps
    1. Read in clinician information
    2. Based on clinician information status, poll their location
    3. Based on poll results, update dictionary
        1. If initialized/within bounds -> query location
        2. If out of bounds -> send alert
        3. If error -> check error count, if error count > ERROR_RETRY_LIMT -> send missing alert
    """
    clinician_geographic_info = None

    try:
        clinician_geographic_info = query_location(clinician.user_id)
        clinician.query_status = check_clinician_within_bounds(
            clinician_geographic_info.curr_point, clinician_geographic_info.bounds
        )
    except Exception as _:
        clinician.query_status = ClinicianStatus.ERROR

    match clinician.query_status:
        case ClinicianStatus.WITHIN_BOUNDS:
            logger.info(f"Clinician {clinician.user_id} within bounds")
            PHLEBOTOMIST_DATA[clinician.user_id]["query_status"] = (
                ClinicianStatus.WITHIN_BOUNDS
            )
            PHLEBOTOMIST_DATA[clinician.user_id]["error_count"] = 0

        case ClinicianStatus.OUT_OF_BOUNDS:
            PHLEBOTOMIST_DATA[clinician.user_id]["query_status"] = (
                ClinicianStatus.OUT_OF_BOUNDS
            )
            PHLEBOTOMIST_DATA[clinician.user_id]["error_count"] = 0

            logger.debug(
                f"Clinician {clinician.user_id} out of bounds. Curr Point: {clinician_geographic_info.curr_point} Bounds: {clinician_geographic_info.bounds}"
            )

            send_alert(
                clinician_id=clinician.user_id,
                alert_case=ClinicianStatus.OUT_OF_BOUNDS,
            )

        case ClinicianStatus.ERROR:
            logger.info(f"Clinician {clinician.user_id} error'd out")
            logger.info(
                f"Clinician retry: {PHLEBOTOMIST_DATA[clinician.user_id]['error_count']}"
            )

            if PHLEBOTOMIST_DATA[clinician.user_id]["error_count"] < ERROR_RETRY_LIMT:
                PHLEBOTOMIST_DATA[clinician.user_id]["error_count"] += 1
                time.sleep(ERROR_POLL_INTERVAL)

                clinician_workflow(clinician)
            else:
                PHLEBOTOMIST_DATA[clinician.user_id]["query_status"] = (
                    ClinicianStatus.ERROR
                )
                send_alert(
                    clinician_id=clinician.user_id, alert_case=ClinicianStatus.ERROR
                )
        case _:
            logger.error(f"Unknown ClinicianStatus: {clinician.query_status}")


async def poll_locations():
    """Task executor for the clinician workflow"""

    logging.info("Polling started")

    start_time = datetime.datetime.now()
    curr_round = 0

    while datetime.datetime.now() < start_time + datetime.timedelta(hours=1):
        for _, clinician_info in PHLEBOTOMIST_DATA.items():
            clinician = ClinicianInfo(**clinician_info)
            clinician_workflow(clinician)

        curr_round += 1
        logger.info(f"Iteration Completed: {curr_round}")
        time.sleep(POLL_INTERVAL)


@app.get("/health")
async def health_check():
    """Health check endpoint for the server."""
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
