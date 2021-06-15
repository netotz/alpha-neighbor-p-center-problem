from anpcp.models.instance import Instance
from typing import Set


def pdp_based(instance: Instance) -> Set[int]:
    vertexes = set(p.index for p in instance.vertexes)
    solution = set(instance.get_farthest_indexes())
    while len(solution) < instance.p:
        index, _ = max((
                (v, min(
                    instance.get_dist(v, s) for s in solution
                ))
                for v in vertexes - solution
            ),
            key=lambda m: m[1]
        )
        solution.add(index)
    return solution
