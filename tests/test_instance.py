from anpcp.models import Vertex, Instance


def test_distances() -> None:
    sample = Instance(
        3, 2,
        [
            Vertex(1, 0, 0),
            Vertex(2, 0, 1),
            Vertex(3, 0, 2),
            Vertex(4, 0, 3)
        ]
    )
    sample.calculate_distances()
    assert sample.distances.tolist() == [
        [0, 1, 2, 3],
        [1, 0, 1, 2],
        [2, 1, 0, 1],
        [3, 2, 1, 0]
    ]
