from typing import Optional, Union

import requests
from shapely import Point, Polygon

from app_logger import logger
from clinicians import ClinicianStatus
from models import Bounds, Location, LocationResponse

PHLEBOTOMIST_API_BASE = "https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test"
ERROR_API_BASE = "http://localhost:3000"


def query_location(clinician_id: int) -> Optional[LocationResponse]:
    """Query the location of a clinician."""

    logger.info(f"Querying location for clinician #{clinician_id}")
    resp = None

    try:
        resp = requests.get(
            f"{PHLEBOTOMIST_API_BASE}/clinicianstatus/{clinician_id}", timeout=5
        )

        if resp.status_code == 200:
            data = resp.json()

            logger.info("Clinician Status API Response: {data}")

            if "features" not in data:
                logger.debug(f"Failed to query location for clinician #{clinician_id}")
                raise requests.exceptions.HTTPError("Failed to query location")

            polygon_points = [
                Location(lat=point[0], lon=point[1])
                for point in data["features"][1]["geometry"]["coordinates"][0]
            ]

            location_info = LocationResponse(
                curr_point=Location(
                    lat=data["features"][0]["geometry"]["coordinates"][0],
                    lon=data["features"][0]["geometry"]["coordinates"][1],
                ),
                bounds=Bounds(limits=polygon_points),
            )

            return location_info
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    ):
        logger.debug(f"Failed to query location for clinician #{clinician_id}")
        if resp:
            logger.debug(f"Status code: {resp.status}")

        raise
    except Exception as e:
        logger.error("Uncaught exception: ", e)
        raise

    return None


def check_clinician_within_bounds(
    location: Location, bounds: Bounds
) -> Union[ClinicianStatus.WITHIN_BOUNDS, ClinicianStatus.OUT_OF_BOUNDS]:
    """Check if a clinician is within bounds given the geographic information"""

    curr_location = Point(location.lat, location.lon)
    curr_bounds = Polygon((i.lat, i.lon) for i in bounds.limits)

    if curr_bounds.contains(curr_location) or curr_bounds.touches(curr_location):
        return ClinicianStatus.WITHIN_BOUNDS

    return ClinicianStatus.OUT_OF_BOUNDS
