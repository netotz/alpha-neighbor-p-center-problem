from dataclasses import dataclass, field
import heapq
import random
from typing import List, Sequence, Set
from itertools import combinations, product, repeat
import timeit

import matplotlib.pyplot as plt

from models.profitable_swap import ProfitableSwap
from models.allocated_facility import AllocatedFacility
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
        self.solution.closed_facilities = self.instance.facilities_indexes - self.solution.open_facilities


    def __init_allocations(self) -> None:
        self.solution.allocations = [
            [0 for _ in range(self.instance.m)]
            for _ in range(self.instance.n)
        ]


    def __allocate_all(self) -> None:
        '''
        Allocates all customers to their alpha-th and beta-th closest facilities.

        Time complexity: O(n (p log p)) ?
        '''
        for customer in self.instance.customers_indexes:
            sorted_facilities = heapq.nsmallest(
                self.alpha + 1,
                (
                    (f, self.instance.get_distance(customer, f))
                    for f in self.solution.open_facilities
                ),
                key=lambda fd: fd[1]
            )

            for i, (k_facility, distance) in enumerate(sorted_facilities[-2:]):
                k = i + self.alpha
                self.allocate(customer, k_facility, k)


    def allocate(self, customer: int, facility: int, kth: int) -> None:
        self.solution.allocations[customer][facility] = kth


    def deallocate(self, customer: int, facility: int) -> None:
        self.allocate(customer, facility, 0)


    def get_kth_closest(self, customer: int, kth: int) -> AllocatedFacility:
        '''
        Gets the k-th closest facility from customer and their distance.

        Time complexity: O(p)
        '''
        for facility in self.solution.open_facilities:
            if self.solution.allocations[customer][facility] == kth:
                break

        distance = self.instance.get_distance(customer, facility)
        return AllocatedFacility(facility, distance)


    def get_alphath(self, customer: int) -> AllocatedFacility:
        return self.get_kth_closest(customer, self.alpha)


    def eval_obj_func(self) -> AllocatedFacility:
        '''
        Evaluates the objective function,
        returning the maximum alpha-th facility
        and the distance to its allocated customer.

        Time complexity: O(pn)
        '''
        return max(
            (
                AllocatedFacility(f, self.instance.distances[c][f])
                if self.solution.allocations[c][f] == self.alpha
                else AllocatedFacility(f, -1)
                for c in self.instance.customers_indexes
                for f in self.solution.open_facilities
            ),
            key=lambda af: af.distance,
        )

        # return AllocatedFacility(max_alphath, distance)


    def update_obj_func(self) -> None:
        allocated_facility = self.eval_obj_func()
        self.solution.max_alphath = allocated_facility.index
        self.solution.objective_function = allocated_facility.distance


    def insert(self, facility: int) -> None:
        self.solution.closed_facilities.discard(facility)
        self.solution.open_facilities.add(facility)


    def remove(self, facility: int) -> None:
        self.solution.open_facilities.discard(facility)
        self.solution.closed_facilities.add(facility)
        
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


    def fast_swap(self) -> Solution:
        '''
        ! Unfinished method.
        '''
        # initialize auxiliary data structures
        gains = list(repeat(0, self.instance.m))
        losses = list(gains)
        extras = [
            [0 for _ in range(self.instance.m)]
            for _ in range(self.instance.m)
        ]


        def update_structures(
                customer: int,
                alphath: AllocatedFacility,
                betath: AllocatedFacility,
                is_undo: bool = False) -> None:
            '''
            * Temporary inner function.
            '''
            sign = -1 if is_undo else 1

            potential_remove = alphath.index
            losses[potential_remove] += sign * (betath.distance - alphath.distance)

            for potential_insert in self.solution.closed_facilities:
                pi_distance = self.instance.get_distance(customer, potential_insert)
                if pi_distance < betath.distance:
                    gains[potential_insert] += sign * (max(0, alphath.distance - pi_distance))
                    extras[potential_insert][potential_remove] += sign * (betath.distance - max(pi_distance, alphath.distance))


        def find_best_swap() -> ProfitableSwap:
            '''
            Time complexity: O(pm)
            '''
            return max(
                (
                    ProfitableSwap(fi, fr, gains[fi] - losses[fr] + extras[fi][fr])
                    for fi in self.solution.closed_facilities
                    for fr in self.solution.open_facilities
                ),
                key=lambda ps: ps.profit
            )


        affecteds = set(self.instance.customers_indexes)

        while True:
            for customer in affecteds:
                alphath = self.get_alphath(customer)
                betath = self.get_kth_closest(customer, self.alpha + 1)
                update_structures(customer, alphath, betath)

            swap = find_best_swap()
            if swap.profit <= 0:
                break

            affecteds.clear()

            for customer in self.instance.customers_indexes:
                alphath = self.get_alphath(customer)
                betath = self.get_kth_closest(customer, self.alpha + 1)

                fi_distance = self.instance.get_distance(customer, swap.facility_in)

                if (alphath.index == swap.facility_out
                        or betath.index == swap.facility_out
                        or fi_distance < betath.distance):
                    affecteds.add(customer)
                    update_structures(customer, alphath, betath, is_undo=True)
            
            self.insert(swap.facility_in)
            self.remove(swap.facility_out)
            # update allocations
        
        self.update_obj_func()


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

        ax.scatter(
            [customer.x for customer in self.instance.customers],
            [customer.y for customer in self.instance.customers],
            color='tab:blue',
            label='Demand points',
            linewidths=0.3,
            alpha=0.8,
            edgecolors='black'
        )
        ax.scatter(
            [facility.x for facility in self.instance.facilities],
            [facility.y for facility in self.instance.facilities],
            color='red',
            label='Centers',
            linewidths=0.3,
            alpha=0.8,
            edgecolors='black'
        )

        for customer in self.instance.customers:
            fi, dist = self.get_alphath(customer.index)
            facility = next(f for f in self.instance.facilities if f.index == fi)
            color = (
                'orange' if fi == self.solution.max_alphath
                            and dist == self.solution.objective_function
                else 'gray'
            )
            ax.plot(
                (customer.x, facility.x),
                (customer.y, facility.y),
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
