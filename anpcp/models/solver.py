from copy import deepcopy
from dataclasses import dataclass, field
import math
import random
from typing import Dict, List, Optional, Sequence, Set
from itertools import product
import timeit

import matplotlib.pyplot as plt
import pandas as pd

from models.moved_facility import MovedFacility
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

        self.init_solution()
        if self.with_random_solution:
            self.randomize_solution()
        else:
            self.solution.closed_facilities = set(self.instance.facilities_indexes)

    def randomize_solution(self) -> Solution:
        self.solution.open_facilities = set(
            random.sample(self.instance.facilities_indexes, self.p)
        )
        self.solution.closed_facilities = (
            self.instance.facilities_indexes - self.solution.open_facilities
        )

        self.allocate_all()
        self.update_obj_func()

        return self.solution

    def __init_allocations(self) -> None:
        self.solution.allocations = [
            [0 for _ in range(self.instance.m)] for _ in range(self.instance.n)
        ]

    def init_solution(self):
        self.solution = Solution()
        self.__init_allocations()

    def allocate_all(self) -> None:
        """
        Allocates all users to their alpha-neighbors.

        Time: O(mn)
        """
        for user in self.instance.users_indexes:
            self.reallocate_user(user)

    def allocate(self, user: int, facility: int, kth: int) -> None:
        self.solution.allocations[user][facility] = kth

    def reallocate_user(self, user: int) -> None:
        """
        Completely reallocates a user to its alpha-neighbors.

        Time: O(m)
        """
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
        # O(m)
        for facility in self.instance.facilities_indexes:
            self.deallocate(user, facility)

    def get_kth_closest(self, user: int, kth: int) -> AllocatedFacility:
        """
        Gets the `kth` closest facility from `user` with its distance
        by checking each (user, facility) pair from allocations matrix.

        If the there's no `kth` in allocations matrix, `NotAllocatedError` is raised.

        To get the alpha-neighbors of `user`, see `get_alpha_neighbors`.

        Time: O(p)
        """
        # O(p)
        for facility in self.solution.open_facilities:
            if self.solution.allocations[user][facility] == kth:
                distance = self.instance.get_distance(user, facility)
                return AllocatedFacility(facility, user, distance)

        raise NotAllocatedError

    def get_alpha_neighbors(self, user: int) -> Dict[int, AllocatedFacility]:
        """
        Gets the closest facilities from `user` up to its center (including it) with their distances
        by checking all (user, facility) pairs from allocations matrix.

        Returns a dictionary with the k-th position as key and an `AllocatedFacility` object as value.

        To get only one facility, see `get_kth_closest`.

        Time: O(p)
        """
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
        """
        Evaluates the objective function of field `solution`.

        Returns the "critical pair", i.e.
        the maximum alpha-th facility and the distance to its allocated user,
        as an `AllocatedFacility` object.

        Time complexity: O(pn)
        """
        return max(
            (self.get_kth_closest(u, self.alpha) for u in self.instance.users_indexes),
            key=lambda af: af.distance,
        )

    def update_obj_func(self) -> None:
        """
        Time O(pn)
        """
        self.solution.critical_allocation = self.eval_obj_func()

    def construct(self, beta: float = 0) -> Solution:
        """
        Randomized Greedy Dispersion (RGD) construction heuristic.

        Time O(mp)
        """
        # distances from each facility to current solution
        # O(m)
        s_dists = [math.inf] * self.instance.m

        solution = Solution()
        # O(m)
        solution.closed_facilities = set(self.instance.facilities_indexes)

        # choose random facility
        last_inserted = random.choice(list(solution.closed_facilities))
        solution.insert(last_inserted)

        # O(mp)
        while len(solution.open_facilities) < self.p:
            facilities: list[MovedFacility] = []
            min_cost = math.inf
            max_cost = -math.inf

            # O(m)
            for fi in solution.closed_facilities:
                s_dists[fi] = min(
                    s_dists[fi], self.instance.facilities_distances[fi][last_inserted]
                )
                facility = MovedFacility(fi, s_dists[fi])

                max_cost = max(max_cost, s_dists[fi])
                min_cost = min(min_cost, s_dists[fi])

                facilities.append(facility)

            threshold = max_cost - beta * (max_cost - min_cost)
            # O(m)
            candidates = [f.index for f in facilities if f.radius >= threshold]
            last_inserted = random.choice(candidates)
            solution.insert(last_inserted)

        self.solution = solution
        # TODO: delegate this method
        self.__init_allocations()
        # O(mn)
        self.allocate_all()
        # O(pn)
        self.update_obj_func()

        return self.solution

    def interchange(self, is_first_improvement: bool) -> Solution:
        """
        Naive Interchange, checks every possible swap.

        Time O(m**2 pn)
        """
        best_radius = current_radius = self.solution.get_obj_func()
        best_fi = best_fr = -1

        moves = 0
        is_improved = True
        while is_improved:
            # O(m**2 pn)
            for fi in self.solution.closed_facilities:
                fi_distance = self.instance.get_distance(
                    self.solution.critical_allocation.user, fi
                )

                if fi_distance >= current_radius:
                    continue

                # O(mpn) = O(p) * O(mn)
                for fr in self.solution.open_facilities:
                    self.solution.swap(fi, fr)
                    # O(mn)
                    self.allocate_all()
                    # O(pn)
                    self.update_obj_func()

                    if self.solution.get_obj_func() < best_radius:
                        best_radius = self.solution.get_obj_func()
                        best_fi = fi
                        best_fr = fr

                        if is_first_improvement:
                            break

                    # if it's best improvement, "restore" base solution
                    # by reverting the swap
                    self.solution.swap(fr, fi)

                is_improved = best_radius < current_radius
                if is_improved and is_first_improvement:
                    break
                # if solution hasn't improved or is best improvement,
                # keep serching (next fi)

            is_improved = best_radius < current_radius
            # apply the move
            if is_improved:
                moves += 1

                if is_first_improvement:
                    current_radius = best_radius
                    # current solution is already best,
                    # because it's the last one updated
                    continue

                self.solution.swap(best_fi, best_fr)
                self.allocate_all()
                self.update_obj_func()

                current_radius = best_radius = self.solution.get_obj_func()

        # when it doesn't improve,
        # it must be updated because the last swap (the "restored")
        # didn't update it
        self.allocate_all()
        self.update_obj_func()
        self.solution.moves = moves

        return self.solution

    def fast_vertex_substitution(self, is_first_improvement: bool) -> Solution:
        """
        Alpha Fast Vertex Substitution (ANPCP) local search heuristic.

        Time O(mpn)
        """

        def move(facility_in: int) -> MovedFacility:
            """
            Determines the best facility to remove if `facility_in` is inserted,
            and the objective function resulting from the swap.

            Time O(pn)
            """
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
                    lost_arg = alphath.distance
                    # store farther distance between fi and a-1
                    same_arg = max(
                        fi_distance,
                        neighbors[self.alpha - 1].distance if self.alpha > 1
                        # or if it's PCP
                        else 0,
                    )
                    curr_obj_func = max(curr_obj_func, same_arg)
                else:
                    # store closer distance between fi and a+1
                    lost_arg = min(fi_distance, neighbors[self.alpha + 1].distance)
                    same_arg = alphath.distance

                largest = MovedFacility(-1, 0)
                second_largest = MovedFacility(-1, 0)

                # O(a)
                for kth, neighbor in neighbors.items():
                    # TODO: refactor skipping a+1
                    # a+1 is not part of the alpha-neighbors as it's farther than alpha
                    if kth == self.alpha + 1:
                        continue

                    j = neighbor.index

                    # alphath is irrelevant if user is attracted by fi
                    if is_attracted and j == alphath.index:
                        continue

                    lost_neighbors[j] = max(lost_neighbors[j], lost_arg)
                    same_neighbors[j] = max(same_neighbors[j], same_arg)

                    if same_neighbors[j] > largest.radius:
                        second_largest = largest
                        largest = MovedFacility(j, same_neighbors[j])

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
                            else largest.radius,
                        ),
                    )
                    for fr in self.solution.open_facilities
                ),
                key=lambda af: af.radius,
            )

            return best_out

        moves = 0
        is_improved = True
        while is_improved:
            current_radius = self.solution.get_obj_func()

            best_radius = current_radius
            best_fi = best_fr = -1

            # O(mpn)
            for fi in self.solution.closed_facilities:
                fi_distance = self.instance.get_distance(
                    self.solution.critical_allocation.user, fi
                )

                if fi_distance >= current_radius:
                    continue

                # O(pn)
                best_move = move(fi)

                # if the move improves (minimizes) objective function
                if best_move.radius < best_radius:
                    best_radius = best_move.radius
                    best_fi = fi
                    best_fr = best_move.index

                    # if is first improvement, apply the swap now
                    if is_first_improvement:
                        break

            is_improved = best_radius < current_radius
            # apply the move
            if is_improved:
                moves += 1

                self.solution.swap(best_fi, best_fr)
                # O(mn)
                self.allocate_all()
                # O(pn)
                self.update_obj_func()

        self.solution.moves = moves

        return self.solution

    def grasp(self, iters: int, beta: float = 0) -> Solution:
        """
        Applies the GRASP metaheuristic to the current solver.

        `iters`: Number of consecutive iterations without improvement to stop the solver.

        `beta`: Value between 0 and 1 for the RCL in the constructive heuristic. Use -1 for a random value.
        """
        best_solution = None
        best_radius = current_radius = math.inf

        total_time = moves = 0

        last_imp = i = iwi = 0
        while iwi < iters:
            self.init_solution()

            start = timeit.default_timer()

            beta_used = random.random() if beta == -1 else beta
            self.construct(beta_used)
            self.fast_vertex_substitution(True)

            total_time += timeit.default_timer() - start

            current_radius = self.solution.get_obj_func()
            if best_solution is None or current_radius < best_radius:
                best_solution = deepcopy(self.solution)
                best_radius = current_radius
                moves += 1

                iwi = 0
                last_imp = i
            else:
                iwi += 1
            i += 1

        self.solution = deepcopy(best_solution)
        self.solution.time = total_time
        self.solution.moves = moves
        self.solution.last_imp = last_imp

        return self.solution

    def grasp_iters_detailed(self, max_iters: int, beta: float) -> pd.DataFrame:
        """
        Modified method for the experiment of calibrating iterations.

        To use GRASP for other purposes, see `grasp`.
        """
        datalist = list()

        best_solution = None
        best_radius = current_radius = math.inf

        total_time = moves = 0

        i = 0
        while i < max_iters:
            self.init_solution()

            start = timeit.default_timer()

            beta_used = random.random() if beta == -1 else beta
            self.construct(beta_used)
            rgd_of = self.solution.get_obj_func()

            self.fast_vertex_substitution(True)
            afvs_of = self.solution.get_obj_func()

            total_time += timeit.default_timer() - start

            current_radius = self.solution.get_obj_func()
            is_new_best = best_solution is None or current_radius < best_radius
            if is_new_best:
                best_solution = deepcopy(self.solution)
                best_radius = current_radius
                moves += 1

            datalist.append(
                (
                    i,
                    beta_used,
                    rgd_of,
                    afvs_of,
                    total_time,
                    is_new_best,
                )
            )

            i += 1

        self.solution = deepcopy(best_solution)
        self.solution.time = total_time
        self.solution.moves = moves

        dataframe = pd.DataFrame(
            datalist,
            columns="iter beta RGD_OF AFVS_OF time is_new_best".split(),
        )
        return dataframe

    def plot(
        self,
        with_annotations: bool = True,
        with_assignments: bool = True,
        axis: bool = False,
        dpi: Optional[int] = None,
        filename: str = "",
    ) -> None:
        fig, ax = plt.subplots()

        # plot users
        ax.scatter(
            [u.x for u in self.instance.users],
            [u.y for u in self.instance.users],
            color="tab:blue",
            label="Users",
            linewidths=0.3,
            alpha=0.8,
            edgecolors="black",
        )

        # plot centers (open facilities)
        if self.solution.open_facilities:
            ax.scatter(
                [
                    f.x
                    for f in self.instance.facilities
                    if f.index in self.solution.open_facilities
                ],
                [
                    f.y
                    for f in self.instance.facilities
                    if f.index in self.solution.open_facilities
                ],
                marker="s",
                color="red",
                label="Centers ($S$)",
                linewidths=0.3,
                alpha=0.8,
                edgecolors="black",
            )

        # plot closed facilities
        ax.scatter(
            [
                f.x
                for f in self.instance.facilities
                if f.index in self.solution.closed_facilities
            ],
            [
                f.y
                for f in self.instance.facilities
                if f.index in self.solution.closed_facilities
            ],
            marker="s",
            color="gray",
            label="Closed facilities",
            linewidths=0.2,
            alpha=0.8,
            edgecolors="black",
        )

        # plot indexes of nodes
        if with_annotations:
            for u in self.instance.users:
                ax.annotate(u.index, (u.x, u.y))

            for f in self.instance.facilities:
                ax.annotate(f.index, (f.x, f.y))

        # plot assignments
        if with_assignments:
            for user in self.instance.users:
                try:
                    alphath = self.get_kth_closest(user.index, self.alpha)
                except NotAllocatedError:
                    continue

                facility = self.instance.facilities[alphath.index]
                color = (
                    "orange"
                    if alphath.index == self.solution.critical_allocation.index
                    and alphath.distance == self.solution.get_obj_func()
                    else "gray"
                )
                ax.plot(
                    (user.x, facility.x),
                    (user.y, facility.y),
                    color=color,
                    linestyle=":",
                    alpha=0.5,
                )

        ax.legend(loc=(1.01, 0))
        if dpi:
            fig.set_dpi(dpi)

        if not axis:
            ax.set_axis_off()

        if filename:
            fig.savefig(filename, bbox_inches="tight")

        plt.show()


def generate_solvers(
    instances: Sequence[Instance],
    p_percentages: Sequence[float],
    alpha_values: Sequence[int],
) -> List[Solver]:
    return [
        Solver(instance, int(instance.m * p), alpha)
        for instance, p, alpha in product(instances, p_percentages, alpha_values)
    ]
