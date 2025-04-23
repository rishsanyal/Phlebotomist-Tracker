from shapely import Point, Polygon

from clinicians import ClinicianStatus
from models import Bounds, Location
from utils import check_clinician_within_bounds

within_bounds = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Point",
                "coordinates": [-122.3561525345, 37.5873025984],
            },
        },
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-122.3561525345, 37.5873025984],
                        [-122.3595428467, 37.5885948602],
                        [-122.3616886139, 37.5899211055],
                        [-122.3638343812, 37.5912813326],
                        [-122.3688554764, 37.5875746554],
                        [-122.3716449738, 37.5832556334],
                        [-122.367181778, 37.5780860808],
                        [-122.3595428467, 37.5750930179],
                        [-122.3482131959, 37.5847520158],
                        [-122.3503589631, 37.5869965331],
                        [-122.3561525345, 37.5873025984],
                    ]
                ],
            },
        },
    ],
}

outside_bounds = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Point",
                "coordinates": [-122.2210121155, 37.4786044252],
            },
        },
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-122.2648715973, 37.4822824675],
                        [-122.2432422638, 37.4822824675],
                        [-122.2432422638, 37.4985590361],
                        [-122.2648715973, 37.4985590361],
                        [-122.2648715973, 37.4822824675],
                    ]
                ],
            },
        },
    ],
}


def test_clinician_within_bounds():
    assert ClinicianStatus.WITHIN_BOUNDS == (
        check_clinician_within_bounds(
            Location(
                lat=within_bounds["features"][0]["geometry"]["coordinates"][0],
                lon=within_bounds["features"][0]["geometry"]["coordinates"][1],
            ),
            Bounds(
                limits=[
                    Location(lat=i[0], lon=i[1])
                    for i in within_bounds["features"][1]["geometry"]["coordinates"][0]
                ]
            ),
        )
    )


def test_clinician_outside_bounds():
    p = Point(outside_bounds["features"][0]["geometry"]["coordinates"])
    b = Polygon(outside_bounds["features"][1]["geometry"]["coordinates"][0])

    assert not b.contains(p)

    assert ClinicianStatus.OUT_OF_BOUNDS == (
        check_clinician_within_bounds(
            Location(
                lat=outside_bounds["features"][0]["geometry"]["coordinates"][0],
                lon=outside_bounds["features"][0]["geometry"]["coordinates"][1],
            ),
            Bounds(
                limits=[
                    Location(lat=i[0], lon=i[1])
                    for i in outside_bounds["features"][1]["geometry"]["coordinates"][0]
                ]
            ),
        )
    )


if __name__ == "__main__":
    test_clinician_within_bounds()
