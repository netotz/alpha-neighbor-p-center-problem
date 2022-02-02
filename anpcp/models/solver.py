from dataclasses import dataclass, field
import random
from typing import List, Sequence, Set, Tuple
from itertools import combinations, product, repeat
import timeit

import matplotlib.pyplot as plt

from models.instance import Instance
from models.solution import Solution


@dataclass
class Solver:
    instance: Instance
    p: int
    alpha: int

    with_random_solution: bool = field(repr=False, default=False)
    solution: Solution = field(init=False, default=None)
    history: List[Solution] = field(init=False, repr=False, default_factory=list)


    def __post_init__(self):
        self.solution = Solution()
        self.__init_allocations()

        if self.with_random_solution:
            self.__randomize_solution()

        if self.solution.open_facilities:
            self.__allocate_all()
            if len(self.solution.open_facilities) >= self.alpha:
                self.update_obj_func()


    def __randomize_solution(self) -> None:
        self.solution.open_facilities = set(
            random.sample(
                self.instance.facilities_indexes,
                self.p
            )
        )


    def __init_allocations(self) -> None:
        self.solution.allocations = list(repeat(
            list(repeat(0, self.instance.m)),
            self.instance.n
        ))


    def __allocate_all(self) -> None:
        '''
        Allocates all customers to their alpha-th and beta-th closest facilities.

        Time complexity: O(np)
        '''
        alpha = self.alpha
        for customer in self.instance.customers_indexes:
            for kth in (alpha, alpha + 1):
                
                
                closest, dist = self.get_kth_closest(customer, kth)
                self.allocate(customer, closest, kth)


    def allocate(self, customer: int, facility: int, kth: int) -> None:
        self.solution.allocations[customer][facility] = kth


    def deallocate(self, customer: int, facility: int) -> None:
        self.allocate(customer, facility, 0)


    def get_kth_closest(self, customer: int, kth: int) -> Tuple[int, int]:
        '''
        Gets the k-th closest facility from customer and their distance.

        Time complexity: O(m)
        '''
        facility = self.solution.allocations[customer].index(kth)
        distance = self.instance.get_distance(customer, facility)
        return facility, distance


    def get_alphath(self, customer: int) -> Tuple[int, int]:
        return self.get_kth_closest(customer, self.alpha)


    def eval_obj_func(self) -> Tuple[int, int]:
        return max(
            (
                (f, self.instance.distances[c][f])
                if self.solution.allocations[c][f] == self.alpha else 0
                for c in self.instance.customers_indexes
                for f in self.instance.facilities_indexes
            ),
            key=lambda ad: ad[1],
        )


    def update_obj_func(self) -> None:
        self.max_alphath, self.objective_function = self.eval_obj_func()


    def insert(self, facility: int) -> None:
        self.solution.open_facilities.add(facility)


    def remove(self, facility: int) -> None:
        self.solution.open_facilities.discard(facility)
        for customer in self.instance.customers_indexes:
            self.deallocate(customer, facility)


    def pdp(self, use_alpha_as_p: bool = False, beta: float = 0, update: bool = True) -> Solution:
        '''
        TODO: Refactor method to use updated fields.
        '''
        solution = Solution(
            self,
            set(self.instance.get_farthest_indexes())
        )

        p = self.alpha if use_alpha_as_p else self.p
        remaining = self.instance.indexes - solution.open_facilities

        while len(solution.open_facilities) < p:
            costs = [
                (v, min(
                    self.instance.get_distance(v, s)
                    for s in solution.open_facilities
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
            solution.open_facilities.add(chosen)
            remaining.discard(chosen)

        solution.update_obj_func()
        if update:
            self.solution = solution

        return solution


    def greedy(self, update: bool = True) -> Solution:
        '''
        TODO: Refactor method to use updated fields.
        '''
        solution = self.pdp(use_alpha_as_p=True, update=False)
        remaining = self.instance.indexes - solution.open_facilities

        while len(solution.open_facilities) < self.p:
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
            solution.open_facilities.add(index)
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
        '''
        TODO: Refactor method to use updated fields.
        '''
        if another_solution:
            best_solution = another_solution
            update = False
        else:
            best_solution = self.solution

        current_solution = best_solution

        is_improved = True
        while is_improved:
            for selecteds in combinations(best_solution.open_facilities, k):
                unselecteds = self.instance.indexes - best_solution.open_facilities
                for indexes in combinations(unselecteds, k):
                    new_solution = Solver.Solution(
                        self,
                        best_solution.open_facilities - set(selecteds) | set(indexes)
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
        best_solution = Solution(self)

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
            if v.index in self.solution.open_facilities:
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
            color = (
                'orange' if fi == self.solution.max_alphath
                            and dist == self.solution.objective_function
                else 'gray'
            )
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
