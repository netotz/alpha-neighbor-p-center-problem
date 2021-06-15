from anpcp.models import Instance, Vertex
import tsplib95


def read_instance(filename: str, p: int, alpha: int) -> Instance:
    problem = tsplib95.load(filename)
    nodes = problem.node_coords if problem.node_coords else problem.display_data
    return Instance(
        p, alpha, [
            Vertex(i, int(x), int(y))
            for i, (x, y) in nodes.items()
        ]
    )
