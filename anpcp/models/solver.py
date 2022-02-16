from dataclasses import dataclass, field
import random
import sys
from typing import Dict, List, Mapping, NoReturn, Sequence, Set
from itertools import product, repeat
import timeit

import matplotlib.pyplot as plt

from models.moved_facility import MovedFacility
from models.profitable_swap import ProfitableSwap
from models.allocated_facility import AllocatedFacility
from models.instance import Instance
from models.solution import Solution


@dataclass
class Solver:
    instance: Instance
    p: int
    alpha: int

    alpha_range: Set[int] = field(init=False, repr=False, default_factory=set)

    with_random_solution: bool = field(repr=False, default=False)
    solution: Solution = field(init=False, default=None)
    history: List[Solution] = field(init=False, repr=False, default_factory=list)


    def __post_init__(self):
        # edge case where alpha=1, it's PCP, so there's no alpha-1
        self.alpha_range = {self.alpha, self.alpha + 1}
        # if it's ANPCP, add alpha-1 to range
        if self.alpha > 1:
            self.alpha_range.add(self.alpha - 1)
        
        self.solution = Solution()
        if self.with_random_solution:
            self.__randomize_solution()

        self.__init_allocations()
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

        Time complexity: O(mn)
        '''
        for customer in self.instance.customers_indexes:
            self.reallocate_customer(customer)


    def allocate(self, customer: int, facility: int, kth: int) -> None:
        self.solution.allocations[customer][facility] = kth


    def reallocate_customer(self, customer: int) -> None:
        '''
        Completely reallocates a customer to its `alphas_range` closest facilities.

        Time complexity: O(m)
        '''
        self.deallocate_customer(customer)

        k = 0
        for facility, distance in self.instance.sorted_distances[customer]:
            if facility in self.solution.open_facilities:
                k += 1
                if k in self.alpha_range:
                    self.allocate(customer, facility, k)
                if k >= self.alpha + 1:
                    break


    def deallocate(self, customer: int, facility: int) -> None:
        self.allocate(customer, facility, 0)


    def deallocate_facility(self, facility: int) -> None:
        for customer in self.instance.customers_indexes:
            self.deallocate(customer, facility)


    def deallocate_customer(self, customer: int) -> None:
        for facility in self.instance.facilities_indexes:
            self.deallocate(customer, facility)


    def get_kth_closest(self, customer: int, kth: int) -> AllocatedFacility:
        '''
        Gets the `kth` closest facility from `customer` with its distance
        by checking each (customer, facility) pair from allocations matrix.

        To get more than facility at the same time, see `get_kths_closests`.

        Time complexity: O(p)
        '''
        for facility in self.solution.open_facilities:
            if self.solution.allocations[customer][facility] == kth:
                break

        distance = self.instance.get_distance(customer, facility)
        return AllocatedFacility(facility, customer, distance)
    

    def get_alpha_range_closests(self, customer: int) -> Dict[int, AllocatedFacility]:
        '''
        Gets the `alpha_range`-ths closest facilities from `customer` with their distances
        by checking all (customer, facility) pairs from allocations matrix.

        Returns a dictionary with the k-th position as key and an `AllocatedFacility` object as value.

        To get only one facility, see `get_kth_closest`.

        Time complexity: O(p)
        '''
        alpha_closests = dict()
        alpha_range = set(self.alpha_range)
        
        for facility in self.solution.open_facilities:
            k = self.solution.allocations[customer][facility]
            if k in alpha_range:
                distance = self.instance.get_distance(customer, facility)
                alpha_closests[k] = AllocatedFacility(facility, customer, distance)

                alpha_range.discard(k)
                # when all kth positions are found
                if not alpha_range:
                    break

        return alpha_closests


    def eval_obj_func(self) -> AllocatedFacility:
        '''
        Evaluates the objective function of field `solution`.
        
        Returns the "critical pair", i.e.
        the maximum alpha-th facility and the distance to its allocated customer,
        as an `AllocatedFacility` object.

        Time complexity: O(pn)
        '''
        return max(
            (
                self.get_kth_closest(c, self.alpha)
                for c in self.instance.customers_indexes
            ),
            key=lambda af: af.distance
        )


    def update_obj_func(self) -> None:
        self.solution.critical_allocation = self.eval_obj_func()


    def insert(self, facility: int) -> None:
        self.solution.closed_facilities.discard(facility)
        self.solution.open_facilities.add(facility)


    def remove(self, facility: int) -> None:
        self.solution.open_facilities.discard(facility)
        self.solution.closed_facilities.add(facility)
        self.deallocate_facility(facility)


    def construct(self) -> NoReturn:
        '''
        TODO: Implement an algorithm to construct a solution from scratch.
        '''
        raise NotImplementedError


    def pmp_fast_swap(self) -> Solution:
        '''
        A fast swap-based local search procedure,
        based from its application for the PMP.
        '''
        # initialize auxiliary data structures, each entry to 0
        gains = list(repeat(0, self.instance.m))
        losses = list(gains)
        extras = [
            [0 for _ in range(self.instance.m)]
            for _ in range(self.instance.m)
        ]


        def update_structures(
                customer: int,
                closests: Mapping[int, AllocatedFacility],
                is_undo: bool = False) -> None:
            '''
            * Temporary inner function.

            Time complexity: O(m - p) = O(m)
            '''
            sign = -1 if is_undo else 1

            fr = closests[self.alpha].index
            losses[fr] += sign * (closests[self.alpha + 1].distance - closests[self.alpha].distance)

            for fi in self.solution.closed_facilities:
                fi_distance = self.instance.get_distance(customer, fi)

                if fi_distance < closests[self.alpha + 1].distance:
                    gains[fi] += sign * max(
                        0,
                        min(
                            # if d(c, fi) < d(c, a-1) < d(c, a),
                            # the alpha-th is now the previous closest
                            closests[self.alpha].distance - closests[self.alpha - 1].distance,
                            # if d(c, a-1) < d(c, fi) < d(c, a),
                            # the alpha-th is now the inserted facility
                            closests[self.alpha].distance - fi_distance
                        ) if self.alpha > 1
                        # if it's PCP
                        else closests[self.alpha].distance - fi_distance
                    )
                    extras[fi][fr] += sign * (
                        closests[self.alpha + 1].distance - max(fi_distance, closests[self.alpha].distance)
                    )


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
            # O(mn + pn) = O(mn)
            for affected in affecteds:
                closests = self.get_alpha_range_closests(affected)
                update_structures(affected, closests)

            # O(pm)
            best_swap = find_best_swap()
            if best_swap.profit <= 0:
                break

            affecteds: Set[int] = set()

            # O(mn + pn) = O(mn)
            for customer in self.instance.customers_indexes:
                fi_distance = self.instance.get_distance(customer, best_swap.facility_in)

                closests = self.get_alpha_range_closests(customer)
                closests_indexes = {c.index for c in closests.values()}

                if (best_swap.facility_out in closests_indexes
                        or fi_distance < closests[self.alpha + 1].distance):
                    affecteds.add(customer)
                    update_structures(customer, closests, is_undo=True)
            
            self.insert(best_swap.facility_in)
            self.remove(best_swap.facility_out)

            # reallocate affected customers
            # O(mn)
            for affected in affecteds:
                self.reallocate_customer(affected)
        
        self.update_obj_func()


    def fast_swap(self) -> Solution:
        '''
        Fast vertex substitution,
        based from its application for the PCP.
        '''
        def move(facility_in: int) -> MovedFacility:
            '''
            Determines the best facility to remove if `facility_in` is inserted,
            and the objective function resulting from the swap.

            Time complexity: O(pn + 3p) = O(pn)
            '''
            # current objective function
            current_of = 0
            unchanged_radii = {fr: 0 for fr in self.solution.open_facilities}
            changed_radii = dict(unchanged_radii)

            # O(pn)
            for customer in self.instance.customers_indexes:
                fi_distance = self.instance.get_distance(customer, facility_in)
                closests = self.get_alpha_range_closests(customer)

                if fi_distance < closests[self.alpha].distance:
                    current_of = max(current_of, fi_distance)
                else:
                    unchanged_radii[closests[self.alpha].index] = max(
                        unchanged_radii[closests[self.alpha].index],
                        closests[self.alpha].distance
                    )

                    changed_radii[closests[self.alpha].index] = max(
                        changed_radii[closests[self.alpha].index],
                        min(
                            fi_distance,
                            closests[self.alpha + 1].distance
                        )
                    )

            g1 = MovedFacility(-1, -sys.maxsize)
            g2 = MovedFacility(-1, -sys.maxsize)
            # O(p)
            for fr, radius in unchanged_radii.items():
                if radius > g1.radius:
                    g2 = MovedFacility(g1.index, g1.radius)
                    g1 = MovedFacility(fr, radius)

            # O(p)
            out = min(
                (
                    MovedFacility(
                        fr,
                        max(
                            current_of,
                            changed_radii[fr],
                            g2.radius if fr == g1.index
                            else g1.radius
                        )
                    )
                    for fr in self.solution.open_facilities
                ),
                key=lambda af: af.radius
            )

            return out


        while True:
            best_of = sys.maxsize
            best_in = -1
            best_out = -1
            
            # O(mpn)
            for fi in self.solution.closed_facilities:
                fi_distance = self.instance.get_distance(
                    self.solution.critical_allocation.customer,
                    fi
                )

                if fi_distance < self.solution.get_objective_function():
                    moved_facility = move(fi)
                    if moved_facility.radius < best_of:
                        best_of = moved_facility.radius
                        best_in = fi
                        best_out = moved_facility.index
            
            if best_of >= self.solution.get_objective_function():
                break

            self.insert(best_in)
            self.remove(best_out)
            self.__allocate_all()
            self.update_obj_func()
        
        return self.solution


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
            [c.x for c in self.instance.customers],
            [c.y for c in self.instance.customers],
            color='tab:blue',
            label='Customers',
            linewidths=0.3,
            alpha=0.8,
            edgecolors='black'
        )
        ax.scatter(
            [
                f.x for f in self.instance.facilities
                if f.index in self.solution.open_facilities
            ],
            [
                f.y for f in self.instance.facilities
                if f.index in self.solution.open_facilities
            ],
            color='red',
            label='Centers',
            linewidths=0.3,
            alpha=0.8,
            edgecolors='black'
        )
        ax.scatter(
            [
                f.x for f in self.instance.facilities
                if f.index in self.solution.closed_facilities
            ],
            [
                f.y for f in self.instance.facilities
                if f.index in self.solution.closed_facilities
            ],
            color='gray',
            label='Closed facilities',
            linewidths=0.2,
            alpha=0.5,
            edgecolors='black'
        )

        for customer in self.instance.customers:
            alphath = self.get_kth_closest(customer.index, self.alpha)
            facility = self.instance.facilities[alphath.index]
            color = (
                'orange' if alphath.index == self.solution.critical_allocation.index
                            and alphath.distance == self.solution.get_objective_function()
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
