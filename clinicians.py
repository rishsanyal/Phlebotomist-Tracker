from enum import Enum


class ClinicianStatus(Enum):
    """Enum representing the status of a clinician"""

    INITIALIZED = 1
    WITHIN_BOUNDS = 2
    OUT_OF_BOUNDS = 3
    ERROR = 4


INITIAL_DATA = {
    1: {
        "user_id": 1,
        "query_status": ClinicianStatus.INITIALIZED,
        "error_count": 0,
    },
    2: {
        "user_id": 2,
        "query_status": ClinicianStatus.INITIALIZED,
        "error_count": 0,
    },
    3: {
        "user_id": 3,
        "query_status": ClinicianStatus.INITIALIZED,
        "error_count": 0,
    },
    4: {
        "user_id": 4,
        "query_status": ClinicianStatus.INITIALIZED,
        "error_count": 0,
    },
    5: {
        "user_id": 5,
        "query_status": ClinicianStatus.INITIALIZED,
        "error_count": 0,
    },
    6: {
        "user_id": 6,
        "query_status": ClinicianStatus.INITIALIZED,
        "error_count": 0,
    },
    7: {
        "user_id": 7,
        "query_status": ClinicianStatus.INITIALIZED,
        "error_count": 0,
    },
}
