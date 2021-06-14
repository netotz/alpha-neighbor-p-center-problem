from anpcp.models.point import Point
from anpcp.models.instance import Instance


def test_distances() -> None:
    sample = Instance(
        3, 2,
        [
            Point(1, 0, 0),
            Point(2, 0, 1),
            Point(3, 0, 2),
            Point(4, 0, 3)
        ]
    )
    sample.calculate_distances()
    assert sample.distances.tolist() == [
        [0, 1, 2, 3],
        [1, 0, 1, 2],
        [2, 1, 0, 1],
        [3, 2, 1, 0]
    ]
