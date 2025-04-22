import os
import signal
import time
from asyncio import create_task
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI

from clinicians import INITIAL_DATA, ClinicianStatus
from email_utils import send_alert
from models import ClinicianInfo
from utils import check_clinician_within_bounds, query_location

# Setting polling to 4 minutes since it gives us enough time to account
# for network errors, emailing errors, etc and to reach our SLA of 5 mins
POLL_INTERVAL = 5
ERROR_POLL_INTERVAL = 1

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


# TODO: Rename this function
def handle_clinician(clinician: ClinicianInfo):
    """handle the status of a clinician
    TODO: Fix documentation everywhere
    """
    clinician_geographic_info = None
    clinician_geographic_info = query_location(clinician.user_id)

    # TODO: Change to Try/Catch
    if clinician_geographic_info:
        clinician.query_status = check_clinician_within_bounds(
            clinician_geographic_info.curr_point, clinician_geographic_info.bounds
        )
    else:
        clinician.query_status = ClinicianStatus.ERROR

    match clinician.query_status:
        case ClinicianStatus.WITHIN_BOUNDS:
            print(f"Clinician {clinician.user_id} within bounds")
            PHLEBOTOMIST_DATA[clinician.user_id]["query_status"] = (
                ClinicianStatus.WITHIN_BOUNDS
            )
            PHLEBOTOMIST_DATA[clinician.user_id]["error_count"] = 0

        case ClinicianStatus.OUT_OF_BOUNDS:
            PHLEBOTOMIST_DATA[clinician.user_id]["query_status"] = (
                ClinicianStatus.OUT_OF_BOUNDS
            )
            print(f"Clinician {clinician.user_id} out of bounds")

            send_alert(
                phlebotomist_id=clinician.user_id,
                alert_case=ClinicianStatus.OUT_OF_BOUNDS,
            )

        case ClinicianStatus.ERROR:
            # print(f"Clinician {clinician.user_id} error'd out")
            # print(
            #     f"Clinician retry: {PHLEBOTOMIST_DATA[clinician.user_id]['error_count']}"
            # )

            if PHLEBOTOMIST_DATA[clinician.user_id]["error_count"] < 5:
                PHLEBOTOMIST_DATA[clinician.user_id]["error_count"] += 1
                time.sleep(ERROR_POLL_INTERVAL)

                handle_clinician(clinician)
            else:
                PHLEBOTOMIST_DATA[clinician.user_id]["query_status"] = (
                    ClinicianStatus.ERROR
                )
                send_alert(
                    phlebotomist_id=clinician.user_id, alert_case=ClinicianStatus.ERROR
                )
        case _:
            print(f"Unknown status: {clinician.query_status}")


async def poll_locations():
    """
    Steps
    1. Read in clinician information -> Make a local dict
    2. Based on clinician information status, poll their location
    3. Based on poll results, update dictionary
        1. If initialized/within bounds -> query location
        2. If out of bounds -> send alert
        3. If error -> check error count, if error count > 3 -> send missing alert
    """

    while True:
        for _, clinician_info in PHLEBOTOMIST_DATA.items():
            clinician = ClinicianInfo(**clinician_info)
            handle_clinician(clinician)

        break
        # time.sleep(POLL_INTERVAL)


# TODO: Check OpenAPI deployment for this
@app.get("/health", tags=["System"])
async def health_check():
    """ "Health check endpoint for the server."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
