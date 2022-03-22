from dataclasses import dataclass, field
import random
import sys
from typing import Dict, List, Mapping, NoReturn, Optional, Sequence, Set
from itertools import product, repeat
import timeit

import matplotlib.pyplot as plt

from models.moved_facility import MovedFacility
from models.profitable_swap import ProfitableSwap
from models.allocated_facility import AllocatedFacility
from models.instance import Instance
from models.solution import Solution


class NotAllocatedError(Exception):
    pass


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
        self.alpha_range = set(range(1, self.alpha + 2))
        
        self.solution = Solution()
        if self.with_random_solution:
            self.__randomize_solution()

        self.__init_allocations()
        if self.solution.open_facilities:
            self.allocate_all()
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


    def allocate_all(self) -> None:
        '''
        Allocates all users to their alpha-neighbors.

        Time: O(mn)
        '''
        for user in self.instance.users_indexes:
            self.reallocate_user(user)


    def allocate(self, user: int, facility: int, kth: int) -> None:
        self.solution.allocations[user][facility] = kth


    def reallocate_user(self, user: int) -> None:
        '''
        Completely reallocates a user to its alpha-neighbors.

        Time: O(m)
        '''
        # O(m)
        self.deallocate_user(user)

        k = 0
        # O(m)
        for facility, distance in self.instance.sorted_distances[user]:
            if facility in self.solution.open_facilities:
                k += 1
                if k > self.alpha + 1:
                    break

                self.allocate(user, facility, k)


    def deallocate(self, user: int, facility: int) -> None:
        self.allocate(user, facility, 0)


    def deallocate_facility(self, facility: int) -> None:
        for user in self.instance.users_indexes:
            self.deallocate(user, facility)


    def deallocate_user(self, user: int) -> None:
        for facility in self.instance.facilities_indexes:
            self.deallocate(user, facility)


    def get_kth_closest(self, user: int, kth: int) -> AllocatedFacility:
        '''
        Gets the `kth` closest facility from `user` with its distance
        by checking each (user, facility) pair from allocations matrix.

        If the there's no `kth` in allocations matrix, `NotAllocatedError` is raised.

        To get the alpha-neighbors of `user`, see `get_alpha_neighbors`.

        Time: O(p)
        '''
        # O(p)
        for facility in self.solution.open_facilities:
            if self.solution.allocations[user][facility] == kth:
                distance = self.instance.get_distance(user, facility)
                return AllocatedFacility(facility, user, distance)
        
        raise NotAllocatedError
    

    def get_alpha_neighbors(self, user: int) -> Dict[int, AllocatedFacility]:
        '''
        Gets the closest facilities from `user` up to its center (including it) with their distances
        by checking all (user, facility) pairs from allocations matrix.

        Returns a dictionary with the k-th position as key and an `AllocatedFacility` object as value.

        To get only one facility, see `get_kth_closest`.

        Time: O(p)
        '''
        alpha_neighbors = dict()
        # O(a)
        alpha_range = set(self.alpha_range)
        
        # O(p)
        for facility in self.solution.open_facilities:
            k = self.solution.allocations[user][facility]
            if k in alpha_range:
                distance = self.instance.get_distance(user, facility)
                alpha_neighbors[k] = AllocatedFacility(facility, user, distance)

                alpha_range.discard(k)
                # when all kth positions are found
                if len(alpha_range) == 0:
                    break

        return alpha_neighbors


    def eval_obj_func(self) -> AllocatedFacility:
        '''
        Evaluates the objective function of field `solution`.
        
        Returns the "critical pair", i.e.
        the maximum alpha-th facility and the distance to its allocated user,
        as an `AllocatedFacility` object.

        Time complexity: O(pn)
        '''
        return max(
            (
                self.get_kth_closest(c, self.alpha)
                for c in self.instance.users_indexes
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
    

    def swap(self, facility_in: int, facility_out: int) -> None:
        '''
        Applies a swap to the solution by inserting `facility_in` to it
        and removing `facility_out` from it,
        then allocates all users by calling `allocate_all()`
        and finally updates the objective function with `update_obj_func()`.
        '''
        self.insert(facility_in)
        self.remove(facility_out)
        self.allocate_all()
        self.update_obj_func()


    def construct(self) -> NoReturn:
        '''
        TODO: Implement an algorithm to construct a solution from scratch.
        '''
        raise NotImplementedError


    def fast_swap(self, is_first_improvement: bool) -> Solution:
        '''
        Fast Vertex Substitution for ANPCP (FVS-A), 
        based from its application for the PCP.

        Time O(mpn)
        '''


        def move(facility_in: int) -> MovedFacility:
            '''
            Determines the best facility to remove if `facility_in` is inserted,
            and the objective function resulting from the swap.

            Time O(pn)
            '''
            # current objective function
            curr_obj_func = 0
            # O(p)
            same_neighbors = {fr: 0 for fr in self.solution.open_facilities}
            # O(p)
            lost_neighbors = {fr: 0 for fr in self.solution.open_facilities}

            # O(pn)
            for user in self.instance.users_indexes:
                fi_distance = self.instance.get_distance(user, facility_in)

                # O(p)
                neighbors = self.get_alpha_neighbors(user)
                alphath = neighbors[self.alpha]

                is_attracted = fi_distance < alphath.distance

                if is_attracted:
                    # store farther distance between fi and a-1
                    farther_dist = max(
                        fi_distance,
                        neighbors[self.alpha - 1].distance
                            if self.alpha > 1
                            # or if it's PCP
                            else 0
                    )
                    curr_obj_func = max(curr_obj_func, farther_dist)
                else:
                    # store closer distance between fi and a+1
                    closer_dist = min(
                        fi_distance,
                        neighbors[self.alpha + 1].distance
                    )

                largest = MovedFacility(-1, 0)
                second_largest = MovedFacility(-1, 0)
                
                # O(a)
                for kth, neighbor in neighbors.items():
                    # TODO: refactor skipping a+1
                    # a+1 is not part of the alpha-neighbors as it's farther than alpha
                    if kth == self.alpha + 1:
                        continue
                    
                    j = neighbor.index

                    if is_attracted:
                        # alphath is irrelevant if user is attracted by fi
                        if j == alphath.index:
                            continue

                        lost_arg = alphath.distance
                        same_arg = farther_dist
                    else:
                        lost_arg = closer_dist
                        same_arg = alphath.distance

                    lost_neighbors[j] = max(lost_neighbors[j], lost_arg)

                    if same_arg > same_neighbors[j]:
                        same_neighbors[j] = same_arg
                        second_largest = largest
                        largest = MovedFacility(j, same_arg)

            # O(p)
            best_out = min(
                (
                    MovedFacility(
                        fr,
                        max(
                            curr_obj_func,
                            lost_neighbors[fr],
                            second_largest.radius
                                if fr == largest.index
                                else largest.radius
                        )
                    )
                    for fr in self.solution.open_facilities
                ),
                key=lambda af: af.radius
            )

            return best_out


        is_improved = True
        while is_improved:
            best_obj_func = self.solution.get_objective_function()
            best_in = -1
            best_out = -1
            
            # O(mpn)
            for fi in self.solution.closed_facilities:
                fi_distance = self.instance.get_distance(
                    self.solution.critical_allocation.user,
                    fi
                )

                if fi_distance < self.solution.get_objective_function():
                    # O(pn)
                    best_move_out = move(fi)

                    # if the move improves (minimizes) objective function
                    if best_move_out.radius < best_obj_func:
                        best_obj_func = best_move_out.radius
                        best_in = fi
                        best_out = best_move_out.index

                        # if is first improvement, apply the swap now
                        if is_first_improvement:
                            break
            
            is_improved = best_obj_func < self.solution.get_objective_function()
            if is_improved:
                self.swap(best_in, best_out)
        
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


    def plot(self, with_annotations: bool = True, axis: bool = True, dpi: Optional[int] = None) -> None:
        fig, ax = plt.subplots()

        ax.scatter(
            [u.x for u in self.instance.users],
            [u.y for u in self.instance.users],
            color='tab:blue',
            label='Users',
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
            marker='s',
            color='red',
            label='Centers ($S$)',
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
            marker='s',
            color='gray',
            label='Closed facilities',
            linewidths=0.2,
            alpha=0.5,
            edgecolors='black'
        )

        if with_annotations:
            for u in self.instance.users:
                ax.annotate(u.index, (u.x, u.y))

            for f in self.instance.facilities:
                ax.annotate(f.index, (f.x, f.y))

        for user in self.instance.users:
            try:
                alphath = self.get_kth_closest(user.index, self.alpha)
            except NotAllocatedError:
                continue
            
            facility = self.instance.facilities[alphath.index]
            color = (
                'orange' if alphath.index == self.solution.critical_allocation.index
                            and alphath.distance == self.solution.get_objective_function()
                else 'gray'
            )
            ax.plot(
                (user.x, facility.x),
                (user.y, facility.y),
                color=color,
                linestyle=':',
                alpha=0.5
            )

        ax.legend(loc=(1.01, 0))
        if dpi:
            fig.set_dpi(dpi)

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
