from anpcp.utils import eval_obj_func
from typing import Set

from models import Instance


def interchange_first(instance: Instance, solution: Set[int]) -> Set[int]:
    max_alphath, obj_func = eval_obj_func(instance, solution)

    is_improved = False
    while is_improved:
        is_improved = False
        for index in instance.indexes - solution:
            new_solution = solution - {max_alphath} | {index}
            new_alphath, new_obj_func = eval_obj_func(instance, new_solution)

            if new_obj_func < obj_func:
                solution = new_solution
                max_alphath = new_alphath
                obj_func = new_obj_func

                is_improved = True
                break

    return solution
