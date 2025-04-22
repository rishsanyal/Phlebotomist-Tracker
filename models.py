from pydantic import BaseModel


class Location(BaseModel):
    """Represents a point on a map."""

    lat: float
    lon: float


class Bounds(BaseModel):
    """Represents bounds on a map."""

    limits: list[Location]


class ClinicianInfo(BaseModel):
    """Represents the status of each clinician."""

    user_id: int
    query_status: int
    error_count: int
    # error_message_sent: bool


class LocationResponse(BaseModel):
    """Represents the location response from Geo API."""

    curr_point: Location
    bounds: Bounds
