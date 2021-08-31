from utils import eval_obj_func
from typing import Set

from models import Instance


def interchange_first(instance: Instance, solution: Set[int]) -> Set[int]:
    max_alphath, obj_func = eval_obj_func(instance, solution)

    is_improved = True
    while is_improved:
        is_improved = False
        for index in instance.indexes - solution:
            new_solution = solution - {max_alphath} | {index}
            new_alphath, new_obj_func = eval_obj_func(instance, new_solution)

            if new_obj_func < obj_func:
                solution = set(new_solution)
                max_alphath = new_alphath
                obj_func = new_obj_func

                is_improved = True
                break

    return solution


def interchange_best(instance: Instance, solution: Set[int]) -> Set[int]:
    max_alphath, obj_func = eval_obj_func(instance, solution)

    is_improved = True
    while is_improved:
        current_best_solution = set(solution)
        current_best_alphath = max_alphath
        current_best_obj_func = obj_func

        for index in instance.indexes - solution:
            new_solution = solution - {max_alphath} | {index}
            new_alphath, new_obj_func = eval_obj_func(instance, new_solution)

            if new_obj_func < current_best_obj_func:
                current_best_solution = set(new_solution)
                current_best_alphath = new_alphath
                current_best_obj_func = new_obj_func

        is_improved = False
        if current_best_obj_func < obj_func:
            solution = set(current_best_solution)
            max_alphath = current_best_alphath
            obj_func = current_best_obj_func
            is_improved = True

    return solution


def interchange_k(instance: Instance, solution: Set[int], is_first: bool) -> Set[int]:
    max_alphath, obj_func = eval_obj_func(instance, solution)

    is_improved = True
    while is_improved:
        current_best_solution = set(solution)
        current_best_alphath = max_alphath
        current_best_obj_func = obj_func

        for index in instance.indexes - solution:
            new_solution = solution - {max_alphath} | {index}
            new_alphath, new_obj_func = eval_obj_func(instance, new_solution)

            if new_obj_func < current_best_obj_func:
                current_best_solution = set(new_solution)
                current_best_alphath = new_alphath
                current_best_obj_func = new_obj_func

                if is_first:
                    break
        
        is_improved = False
        if current_best_obj_func < obj_func:
            solution = set(current_best_solution)
            max_alphath = current_best_alphath
            obj_func = current_best_obj_func
            is_improved = True

    return solution
