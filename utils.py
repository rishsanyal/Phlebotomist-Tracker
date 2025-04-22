from datetime import datetime
from typing import Union

import requests
from shapely import Point, Polygon

from clinicians import ClinicianStatus
from models import Bounds, Location, LocationResponse

# PHLEBOTOMIST_API_BASE = "https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test"
PHLEBOTOMIST_API_BASE = "http://localhost:3000"


def query_location(phlebotomist_id: int) -> LocationResponse | None:
    """Query the location of a phlebotomist."""

    print(f"Querying location for phlebotomist #{phlebotomist_id}")

    try:
        # TODO: ENHANCEMENT: Instead of 1 request: Make 3 requests together
        resp = requests.get(
            f"{PHLEBOTOMIST_API_BASE}/clinicianstatus/{phlebotomist_id}", timeout=5
        )

        if resp.status_code == 200:
            data = resp.json()

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
    ) as e:
        print(e)
        return None

    print(f"Failed to query location for phlebotomist #{phlebotomist_id}")
    print(f"Status code: {resp.status}")

    ## TODO: Raise an error here
    return None


def check_clinician_within_bounds(
    location: Location, bounds: Bounds
) -> Union[ClinicianStatus.WITHIN_BOUNDS, ClinicianStatus.OUT_OF_BOUNDS]:
    """Check if a clinician is within bounds given the grographic information"""

    curr_location = Point(location.lat, location.lon)
    curr_bounds = Polygon((i.lat, i.lon) for i in bounds.limits)

    if curr_bounds.contains(curr_location) or curr_bounds.touches(curr_location):
        return ClinicianStatus.WITHIN_BOUNDS

    return ClinicianStatus.OUT_OF_BOUNDS
