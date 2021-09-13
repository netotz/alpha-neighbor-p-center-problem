import random
from typing import Set, Tuple
from itertools import combinations

from models import Instance


class Solver:
    def __init__(self, instance: Instance, with_random_solution: bool = False) -> None:
        self.instance = instance
        self.objective_function = -1
        self.max_alphath = -1
        if with_random_solution:
            self.set_random_solution()
        else:
            self.solution = set()


    def set_random_solution(self) -> None:
        self.solution = set(random.sample(self.instance.indexes, self.instance.p))
        self.update_obj_func()


    def get_alphath(self, fromindex: int, another_solution: Set[int] = None) -> Tuple[int, int]:
        solution = another_solution or self.solution
        alphath = self.instance.alpha
        for node, dist in self.instance.sorted_dist[fromindex]:
            if node in solution:
                alphath -= 1
                if alphath == 0:
                    return node, dist


    def eval_obj_func(self, another_solution: Set[int] = None) -> Tuple[int, int]:
        solution = another_solution or self.solution
        return max(
            (
                self.get_alphath(v, solution)
                for v in self.instance.indexes - solution
            ),
            key=lambda a: a[1]
        )


    def update_obj_func(self) -> None:
        self.max_alphath, self.objective_function = self.eval_obj_func()


    def pdp_based(self, use_alpha_as_p: bool = False, update: bool = True) -> Set[int]:
        solution = set(self.instance.get_farthest_indexes())
        p = self.instance.alpha if use_alpha_as_p else self.instance.p
        while len(solution) < p:
            index, dist = max((
                    (v, min(
                        self.instance.get_dist(v, s) for s in solution
                    ))
                    for v in self.instance.indexes - solution
                ),
                key=lambda m: m[1]
            )
            solution |= {index}

        if update:
            self.solution = solution
            self.update_obj_func()

        return solution


    def greedy(self, update: bool = True) -> Set[int]:
        solution = self.pdp_based(use_alpha_as_p=True, update=False)
        while len(solution) < self.instance.p:
            index, dist = min(
                (
                    (
                        v,
                        self.eval_obj_func(solution | {v})[1]
                    )
                    for v in self.instance.indexes - solution
                ),
                key=lambda m: m[1]
            )
            solution |= {index}

        if update:
            self.solution = solution
            self.update_obj_func()

        return solution


    def interchange(self, is_first: bool, k: int = 1, update: bool = True) -> Set[int]:
        best_solution = set(self.solution)
        best_max_alphath = self.max_alphath
        best_obj_func = self.objective_function

        unselecteds = self.instance.indexes - best_solution

        current_solution = set(best_solution)
        current_alphath = best_max_alphath
        current_obj_func = best_obj_func

        is_improved = True
        while is_improved:
            for selecteds in combinations(best_solution, k):
                for indexes in combinations(unselecteds, k):
                    new_solution = best_solution - set(selecteds) | set(indexes)
                    new_alphath, new_obj_func = self.eval_obj_func(new_solution)

                    if new_obj_func < current_obj_func:
                        current_solution = set(new_solution)
                        current_alphath = new_alphath
                        current_obj_func = new_obj_func

                        if is_first:
                            break

                is_improved = current_obj_func < best_obj_func
                if is_improved:
                    best_solution = set(current_solution)
                    best_max_alphath = current_alphath
                    best_obj_func = current_obj_func

                    unselecteds = self.instance.indexes - best_solution
                    # explore another neighborhood
                    break

        if update:
            self.solution = best_solution
            self.max_alphath = best_max_alphath
            self.objective_function = best_obj_func

        return best_solution
