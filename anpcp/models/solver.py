from dataclasses import dataclass, field
import sys
import random
from typing import List, Sequence, Set, Tuple
from itertools import combinations, product
import timeit

import matplotlib.pyplot as plt
import numpy as np

from models import Instance


@dataclass
class Solver:
    @dataclass
    class Solution:
        _solver: 'Solver' = field(repr=False)
        indexes: Set[int] = field(default_factory=set)
        objective_function: int = field(init=False, default=sys.maxsize)
        allocations: np.ndarray = field(init=False, default=None)
        max_alphath: int = field(init=False, default=-1)
        time: float = field(init=False, repr=False, default=-1)


        def __post_init__(self):
            n = self._solver.instance.n
            self.allocations = np.zeros((n, n), dtype=int)

            if self.indexes:
                self.allocate()
                if len(self.indexes) >= self._solver.alpha:
                    self.update_obj_func()


        def set_random(self) -> None:
            self.indexes = set(
                random.sample(
                    self._solver.instance.indexes,
                    self._solver.p
                )
            )
            self.update_obj_func()


        def allocate(self):
            alpha = self._solver.alpha
            for index in self._solver.instance.indexes:
                for nth in (alpha, alpha + 1):
                    closest, dist = self.get_n_closest(nth, index)
                    self.allocations[index, closest] = nth


        def get_n_closest(self, n: int, fromindex: int) -> Tuple[int, int]:
            nth = n
            for node, dist in self._solver.instance.sorted_dist[fromindex]:
                if node in self.indexes:
                    nth -= 1
                    if nth == 0:
                        return node, dist


        def get_alphath(self, fromindex: int) -> Tuple[int, int]:
            return self.get_n_closest(self._solver.alpha, fromindex)


        def eval_obj_func(self) -> Tuple[int, int]:
            n = self.allocations.shape[0]
            return max(
                self._solver.instance.distances[i, j]
                if self.allocations[i, j] == self._solver.alpha else 0
                for i in range(n)
                for j in range(n)
            )


        def update_obj_func(self) -> None:
            self.max_alphath, self.objective_function = self.eval_obj_func()


    instance: Instance
    p: int
    alpha: int
    with_random_solution: bool = field(repr=False, default=False)
    solution: Solution = field(init=False)
    history: List[Solution] = field(init=False, repr=False, default_factory=list)


    def __post_init__(self):
        self.solution = Solver.Solution(self)
        if self.with_random_solution:
            self.solution.set_random()


    def pdp(self, use_alpha_as_p: bool = False, beta: float = 0, update: bool = True) -> Solution:
        solution = Solver.Solution(
            self,
            set(self.instance.get_farthest_indexes())
        )

        p = self.alpha if use_alpha_as_p else self.p
        remaining = self.instance.indexes - solution.indexes

        while len(solution.indexes) < p:
            costs = [
                (v, min(
                    self.instance.get_dist(v, s)
                    for s in solution.indexes
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
                    new_solution = Solver.Solution(
                        self,
                        best_solution.indexes - set(selecteds) | set(indexes)
                    )

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
            start = timeit.default_timer()

            current_solution = self.pdp(beta=beta, update=False)
            current_solution = self.interchange(
                is_first=True,
                another_solution=current_solution
            )

            current_solution.time = timeit.default_timer() - start
            self.history.append(current_solution)

            if current_solution.objective_function < best_solution.objective_function:
                best_solution = current_solution

            i += 1

        if update:
            self.solution = best_solution

        return best_solution


    def plot(self, axis: bool = True) -> None:
        fig, ax = plt.subplots()

        clients = list()
        facilities = list()
        for v in self.instance.vertexes:
            if v.index in self.solution.indexes:
                facilities.append(v)
            else:
                clients.append(v)

        ax.scatter(
            [c.x for c in clients],
            [c.y for c in clients],
            color='tab:blue',
            label='Demand points',
            linewidths=0.3,
            alpha=0.8,
            edgecolors='black'
        )
        ax.scatter(
            [f.x for f in facilities],
            [f.y for f in facilities],
            color='red',
            label='Centers',
            linewidths=0.3,
            alpha=0.8,
            edgecolors='black'
        )

        for c in clients:
            fi, dist = self.solution.get_alphath(c.index)
            facility = next(f for f in facilities if f.index == fi)
            color = ('orange'
                if fi == self.solution.max_alphath and
                    dist == self.solution.objective_function
                else 'gray')
            ax.plot(
                (c.x, facility.x),
                (c.y, facility.y),
                color=color,
                linestyle=':',
                alpha=0.5
            )

        ax.legend(loc=(1.01, 0))
        fig.set_dpi(250)

        if not axis:
            ax.set_axis_off()
        plt.show()


def generate_solvers(
        instances: Sequence[Instance],
        p_percentages: Sequence[float],
        alpha_values: Sequence[int]) -> List[Solver]:
    return [
        Solver(instance, int(instance.n * p), alpha)
        for instance, p, alpha in product(instances, p_percentages, alpha_values)
    ]
