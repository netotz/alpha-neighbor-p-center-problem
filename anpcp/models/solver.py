from dataclasses import dataclass, field
import sys
import random
from typing import List, Sequence, Set, Tuple
from itertools import combinations, product

from models import Instance


class Solver:
    @dataclass
    class Solution:
        _solver: 'Solver'
        indexes: Set[int] = field(default_factory=set)
        objective_function: int = sys.maxsize
        max_alphath: int = -1


        def set_random(self) -> None:
            self.indexes = set(
                random.sample(
                    self._solver.instance.indexes,
                    self._solver.p
                )
            )
            self.update_obj_func()

        def eval_obj_func(self) -> Tuple[int, int]:
            def get_alphath(fromindex: int) -> Tuple[int, int]:
                alphath = self._solver.alpha
                for node, dist in self._solver.instance.sorted_dist[fromindex]:
                    if node in self.indexes:
                        alphath -= 1
                        if alphath == 0:
                            return node, dist

            return max(
                (
                    get_alphath(v)
                    for v in self._solver.instance.indexes - self.indexes
                ),
                key=lambda a: a[1]
            )


        def update_obj_func(self) -> None:
            self.max_alphath, self.objective_function = self.eval_obj_func()


    def __init__(
            self,
            instance: Instance,
            p: int,
            alpha: int,
            with_random_solution: bool = False) -> None:
        self.instance = instance
        self.p = p
        self.alpha = alpha
        self.solution = Solver.Solution(self)
        if with_random_solution:
            self.solution.set_random()


    def pdp(self, use_alpha_as_p: bool = False, beta: float = 0, update: bool = True) -> Solution:
        solution = Solver.Solution(self)
        solution.indexes = set(self.instance.get_farthest_indexes())

        p = self.alpha if use_alpha_as_p else self.p
        remaining = self.instance.indexes - solution.indexes

        while len(solution.indexes) < p:
            costs = [
                (v, min(
                    self.instance.get_dist(v, s) for s in solution.indexes
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
            solution.indexes.add(chosen)
            remaining.discard(chosen)

        solution.update_obj_func()
        if update:
            self.solution = solution

        return solution


    def greedy(self, update: bool = True) -> Solution:
        solution = Solver.Solution(self)
        solution = self.pdp(use_alpha_as_p=True, update=False)
        remaining = self.instance.indexes - solution.indexes
        while len(solution.indexes) < self.p:
            index, dist = min(
                (
                    (
                        v,
                        # TODO: Refactor method
                        solution.eval_obj_func(solution | {v})[1]
                    )
                    for v in remaining
                ),
                key=lambda m: m[1]
            )
            solution.indexes.add(index)
            remaining.discard(index)

        solution.update_obj_func()
        if update:
            self.solution = solution

        return solution


    def interchange(
            self,
            is_first: bool,
            k: int = 1,
            another_solution: Solution = None,
            update: bool = True) -> Solution:
        if another_solution:
            best_solution = another_solution
            update = False
        else:
            best_solution = self.solution

        current_solution = best_solution

        is_improved = True
        while is_improved:
            for selecteds in combinations(best_solution.indexes, k):
                unselecteds = self.instance.indexes - best_solution.indexes
                for indexes in combinations(unselecteds, k):
                    new_solution = Solver.Solution(self)
                    new_solution.indexes = best_solution.indexes - set(selecteds) | set(indexes)
                    new_solution.update_obj_func()

                    if new_solution.objective_function < current_solution.objective_function:
                        current_solution = new_solution

                        if is_first:
                            break

                is_improved = current_solution.objective_function < best_solution.objective_function
                if is_improved:
                    best_solution = current_solution

                    # explore another neighborhood
                    break

        if update:
            self.solution = best_solution

        return best_solution


    def grasp(self, max_iters: int, beta: float = 0, update: bool = True) -> Set[int]:
        '''
        Applies the GRASP metaheuristic to the current solver.

        `max_iters`: Maximum number of iterations until returning the best found solution.

        `beta`: Value between 0 and 1 for the RCL in the constructive heuristic.
        '''
        best_solution = Solver.Solution(self)
        i = 0
        while i < max_iters:
            current_solution = Solver.Solution(self)
            current_solution = self.pdp(beta=beta, update=False)
            current_solution = self.interchange(
                is_first=True,
                another_solution=current_solution
            )
            current_solution.update_obj_func()

            if current_solution.objective_function < best_solution.objective_function:
                best_solution = current_solution
            i += 1

        if update:
            self.solution = best_solution

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
