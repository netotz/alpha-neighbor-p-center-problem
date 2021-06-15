from typing import Set

from anpcp.utils import eval_obj_func
from anpcp.models import Instance

def pdp_based(instance: Instance, use_alpha_as_p: bool = False) -> Set[int]:
    solution = set(instance.get_farthest_indexes())
    p = instance.alpha if use_alpha_as_p else instance.p
    while len(solution) < p:
        index, dist = max((
                (v, min(
                    instance.get_dist(v, s) for s in solution
                ))
                for v in instance.indexes - solution
            ),
            key=lambda m: m[1]
        )
        solution |= {index}
    return solution


def greedy(instance: Instance) -> Set[int]:
    solution = pdp_based(instance, use_alpha_as_p=True)
    while len(solution) < instance.p:
        index, dist = min((
                (v, eval_obj_func(instance, solution | {v}))
                for v in instance.indexes - solution
            ),
            key=lambda m: m[1]
        )
        solution |= {index}
    return solution
