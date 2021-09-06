from typing import Set, Tuple
from models import Instance


def eval_obj_func(instance: Instance, solution: Set[int]) -> Tuple[int, int]:
    return max(
        (
            instance.get_alphath(v, solution)
            for v in instance.indexes - solution
        ),
        key=lambda a: a[1]
    )
