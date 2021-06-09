from anpcp.models import Instance, Point
import tsplib95


def read_instance(filename: str, alpha: int, p: int) -> Instance:
    problem = tsplib95.load(filename)
    nodes = problem.node_coords if problem.node_coords else problem.display_data
    points = [
        Point(i, coords[0], coords[1])
        for i, coords in nodes.items()
    ]
    return Instance(alpha, p, points)
