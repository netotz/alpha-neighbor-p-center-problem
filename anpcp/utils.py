import itertools
from typing import Set

import tsplib95

from models import Instance, Vertex


def read_instance(filename: str, p: int, alpha: int) -> Instance:
    problem = tsplib95.load(filename)
    nodes = problem.node_coords if problem.node_coords else problem.display_data
    return Instance(
        p, alpha, [
            Vertex(i, int(x), int(y))
            for i, (x, y) in nodes.items()
        ]
    )


def eval_obj_func(instance: Instance, solution: Set[int]) -> int:
    return max(
        min(
            max(instance.get_dist(v, s) for s in subset)
            for subset in itertools.combinations(solution, instance.alpha)
        )
        for v in instance.indexes - solution
    )
