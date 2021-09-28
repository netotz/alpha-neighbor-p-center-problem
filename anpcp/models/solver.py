import sys
import random
from typing import ByteString, List, Sequence, Set, Tuple
from itertools import combinations, product

from models import Instance


class Solver:
    def __init__(
            self,
            instance: Instance,
            p: int,
            alpha: int,
            with_random_solution: bool = False) -> None:
        self.instance = instance
        self.p = p
        self.alpha = alpha
        self.objective_function = None
        self.max_alphath = None
        self.solution = set()
        if with_random_solution:
            self.set_random_solution()


    def set_random_solution(self) -> None:
        self.solution = set(random.sample(self.instance.indexes, self.p))
        self.update_obj_func()


    def get_alphath(self, fromindex: int, another_solution: Set[int] = None) -> Tuple[int, int]:
        solution = another_solution or self.solution
        alphath = self.alpha
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


    def pdp(self, use_alpha_as_p: bool = False, beta: int = 0, update: bool = True) -> Set[int]:
        solution = set(self.instance.get_farthest_indexes())
        p = self.alpha if use_alpha_as_p else self.p
        remaining = self.instance.indexes - solution
        while len(solution) < p:
            costs = [
                (v, min(
                    self.instance.get_dist(v, s) for s in solution
                ))
                for v in remaining
            ]
            min_cost = min(costs, key=lambda c: c[1])[1]
            max_cost = max(costs, key=lambda c: c[1])[1]
            candidates = [
                v for v, c in costs
                if c >= max_cost - beta * (max_cost - min_cost)
            ]
            chosen = random.choice(candidates)
            solution.add(chosen)
            remaining.discard(chosen)

        if update:
            self.solution = solution
            self.update_obj_func()

        return solution


    def greedy(self, update: bool = True) -> Set[int]:
        solution = self.pdp(use_alpha_as_p=True, update=False)
        remaining = self.instance.indexes - solution
        while len(solution) < self.p:
            index, dist = min(
                (
                    (
                        v,
                        self.eval_obj_func(solution | {v})[1]
                    )
                    for v in remaining
                ),
                key=lambda m: m[1]
            )
            solution.add(index)
            remaining.discard(index)

        if update:
            self.solution = solution
            self.update_obj_func()

        return solution


    def interchange(
            self,
            is_first: bool,
            k: int = 1,
            another_solution: Set[int] = None,
            update: bool = True) -> Set[int]:
        if another_solution:
            best_solution = another_solution
            best_max_alphath, best_obj_func = self.eval_obj_func(another_solution)
        else:
            best_solution = self.solution
            best_max_alphath = self.max_alphath
            best_obj_func = self.objective_function

        current_solution = best_solution
        current_alphath = best_max_alphath
        current_obj_func = best_obj_func

        is_improved = True
        while is_improved:
            for selecteds in combinations(best_solution, k):
                unselecteds = self.instance.indexes - best_solution
                for indexes in combinations(unselecteds, k):
                    new_solution = best_solution - set(selecteds) | set(indexes)
                    new_alphath, new_obj_func = self.eval_obj_func(new_solution)

                    if new_obj_func < current_obj_func:
                        current_solution = new_solution
                        current_alphath = new_alphath
                        current_obj_func = new_obj_func

                        if is_first:
                            break

                is_improved = current_obj_func < best_obj_func
                if is_improved:
                    best_solution = current_solution
                    best_max_alphath = current_alphath
                    best_obj_func = current_obj_func

                    # explore another neighborhood
                    break

        if update:
            self.solution = best_solution
            self.max_alphath = best_max_alphath
            self.objective_function = best_obj_func

        return best_solution


    def grasp(self, max_iters: int, beta: int = 0, update: bool = True) -> Set[int]:
        best_solution = set()
        best_obj_func = sys.maxsize
        best_max_alphath = -1
        i = 0
        while i < max_iters:
            solution = self.pdp(beta=beta, update=False)
            solution = self.interchange(
                is_first=True,
                another_solution=solution,
                update=False
            )
            max_alphath, obj_func = self.eval_obj_func(solution)
            if obj_func < best_obj_func:
                best_solution = solution
                best_obj_func = obj_func
                best_max_alphath = max_alphath
            i += 1

        if update:
            self.solution = best_solution
            self.objective_function = best_obj_func
            self.max_alphath = best_max_alphath

        return best_solution


def generate_solvers(
        instances: Sequence[Instance],
        p_percentages: Sequence[float],
        alpha_values: Sequence[int]) -> List[Solver]:
    return [
        Solver(instance, int(instance.n * p), alpha)
        for p, alpha in product(p_percentages, alpha_values)
        for instance in instances
    ]
