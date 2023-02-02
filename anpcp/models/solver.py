from copy import deepcopy
from dataclasses import dataclass, field
import math
import random
from typing import Dict, List, Sequence, Set
import timeit

import pandas as pd

from models.moved_facility import MovedFacility
from models.allocated_facility import AllocatedFacility
from models.instance import Instance
from models.solution import Solution
from models.min_max_avg import MinMaxAvg


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
        self.set_alpha_range()

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

    def set_alpha_range(self):
        self.alpha_range = set(range(1, self.alpha + 2))

    @classmethod
    def from_solver(cls, solver: "Solver"):
        """
        Returns a shallow copy of `solver`.
        This method was created to get an instance of a derived solver,
        like `GraspFinalSolver`.
        """
        return cls(solver.instance, solver.p, solver.alpha)

    def get_users_indexes(self) -> Set[int]:
        return self.instance.users_indexes

    def allocate_all(self) -> None:
        """
        Allocates all users to their alpha-neighbors.

        If users and facilities are same set of points,
        the rows for the centers won't be updated in allocations matrix.
        This is safe because only closed facilities (users) are accessed.

        Time: O(mn)
        """
        for user in self.get_users_indexes():
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
        for facility in self.instance.next_nearest_facility(user):
            # this condition should also be true when F an U are same set,
            # because `user` is a closed facility and therefore `facility` too
            if facility not in self.solution.open_facilities:
                continue

            k += 1
            if k > self.alpha + 1:
                break

            self.allocate(user, facility, k)

    def deallocate(self, user: int, facility: int) -> None:
        self.allocate(user, facility, 0)

    def deallocate_user(self, user: int) -> None:
        # O(m)
        for facility in self.instance.facilities_indexes:
            self.deallocate(user, facility)

    def get_kth_closest(self, user: int, kth: int) -> AllocatedFacility:
        """
        Gets the `kth` closest facility from `user` with its distance.

        Raises `NotAllocatedError` if there's no `kth` in allocations matrix.

        To get the alpha-neighbors of `user`, see `get_alpha_neighbors`.

        Time: O(p)
        """
        # O(p)
        for facility in self.solution.open_facilities:
            if self.solution.allocations[user][facility] != kth:
                continue

            return AllocatedFacility(
                facility, user, self.instance.get_distance(user, facility)
            )

        raise NotAllocatedError

    def get_alpha_neighbors(self, user: int) -> Dict[int, AllocatedFacility]:
        """
        Gets the closest facilities from `user` up to its center (including it) with their distances.

        Returns a dictionary with the k-th position as key and an `AllocatedFacility` object as value.

        To get only one facility, see `get_kth_closest`.

        Time: O(p)
        """
        alpha_neighbors = dict()
        # O(a)
        temp_alpha_range = set(self.alpha_range)

        # O(p)
        for facility in self.solution.open_facilities:
            k = self.solution.allocations[user][facility]

            if k not in temp_alpha_range:
                continue

            distance = self.instance.get_distance(user, facility)
            alpha_neighbors[k] = AllocatedFacility(facility, user, distance)

            temp_alpha_range.discard(k)
            # when all kth positions are found
            if len(temp_alpha_range) == 0:
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
            (self.get_kth_closest(u, self.alpha) for u in self.get_users_indexes()),
            key=lambda af: af.distance,
        )

    def update_obj_func(self) -> None:
        """
        Time O(pn)
        """
        self.solution.critical_allocation = self.eval_obj_func()

    def apply_swap(self, facility_in, facility_out) -> None:
        """
        Inserts `facility_in` into solution, removes `facility_out` from it,
        and updates allocations and objective function.

        Time O(mn + pn) ~= O(mn) since m > p
        """
        self.solution.swap(facility_in, facility_out)
        # O(mn)
        self.allocate_all()
        # O(pn)
        self.update_obj_func()

    def reset_alpha(self, new_alpha: int) -> None:
        """
        Resets this solver with `new_alpha` as the alpha parameter,
        keeping the same solution.
        """
        self.alpha = new_alpha
        self.set_alpha_range()
        self.allocate_all()
        self.update_obj_func()

    def get_users_per_center_stats(self):
        n = len(self.solution.allocations)

        min_users = math.inf
        max_users = -math.inf
        users_sum = 0

        for center in self.solution.open_facilities:
            users = sum(
                self.solution.allocations[user][center] == self.alpha
                for user in range(n)
            )

            min_users = min(min_users, users)
            max_users = max(max_users, users)
            users_sum += users

        avg_users = users_sum / self.p
        return MinMaxAvg(min_users, max_users, avg_users)

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
        Greedy Interchange, checks every possible swap.

        Time O(m**2 pn)
        """
        best_radius = current_radius = self.solution.get_obj_func()
        best_fi = best_fr = -1

        moves = 0
        is_improved = True
        while is_improved:
            ## O(m**2 pn)
            # O(m - p) ~= O(m)
            for fi in self.solution.closed_facilities:
                fi_distance = self.instance.get_distance(
                    self.solution.critical_allocation.user, fi
                )

                if fi_distance >= current_radius:
                    continue

                ## O(mpn)
                # O(p)
                for fr in self.solution.open_facilities:
                    # O(mn)
                    self.apply_swap(fi, fr)

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

                # O(mn)
                self.apply_swap(best_fi, best_fr)

                current_radius = best_radius = self.solution.get_obj_func()

        # when it doesn't improve,
        # it must be updated because the last swap (the "restored")
        # didn't update it
        self.allocate_all()
        self.update_obj_func()
        self.solution.moves = moves

        return self.solution

    def move(self, facility_in: int) -> MovedFacility:
        """
        Determines the best facility to remove if `facility_in` is inserted,
        and the objective function resulting from the swap.

        Time O(pn)
        """
        # best objective function so far
        best_radius = 0
        # O(p)
        same_neighbors = {fr: 0 for fr in self.solution.open_facilities}
        # O(p)
        lost_neighbors = {fr: 0 for fr in self.solution.open_facilities}

        largest = MovedFacility(-1, 0)
        second_largest = MovedFacility(-1, 0)

        ## O(n(p + a)) ~= O(pn) since p > a
        # O(n)
        for user in self.get_users_indexes():
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
                best_radius = max(best_radius, same_arg)
            else:
                # store closer distance between fi and a+1
                lost_arg = min(fi_distance, neighbors[self.alpha + 1].distance)
                same_arg = alphath.distance

            # skip a+1 because is not in alpha-neighbors
            neighbors.pop(self.alpha + 1)
            # O(a) ~= O(1) since alpha is usually very small
            for neighbor in neighbors.values():
                current_index = neighbor.index

                # alphath is irrelevant if user is attracted to fi
                if is_attracted and current_index == alphath.index:
                    continue

                lost_neighbors[current_index] = max(
                    lost_neighbors[current_index], lost_arg
                )
                same_neighbors[current_index] = max(
                    same_neighbors[current_index], same_arg
                )

                if same_neighbors[current_index] > largest.radius:
                    second_largest = largest
                    largest = MovedFacility(
                        current_index, same_neighbors[current_index]
                    )

        # O(p)
        best_out = min(
            (
                MovedFacility(
                    fr,
                    max(
                        best_radius,
                        lost_neighbors[fr],
                        second_largest.radius
                        if fr == largest.index
                        else largest.radius,
                    ),
                )
                for fr in self.solution.open_facilities
            ),
            key=lambda mf: mf.radius,
        )

        return best_out

    def try_improve(self, is_first_improvement: bool) -> bool:
        """
        Returns `True` if `self.solution` was improved (objective function was minimized)
        by searching for the best facility to insert and the best to remove.
        If no possible move improves the current solution, returns `False`.

        Time O(mpn)
        """

        current_radius = self.solution.get_obj_func()

        best_radius = current_radius
        best_fi = best_fr = -1

        ## O(mpn)
        # O(m - p) ~= O(m) since m > p
        for fi in self.solution.closed_facilities:
            fi_distance = self.instance.get_distance(
                self.solution.critical_allocation.user, fi
            )

            if fi_distance >= current_radius:
                continue

            # O(pn)
            best_move = self.move(fi)
            fr = best_move.index
            radius = best_move.radius

            # if move improves S (minimizes objective function)
            if radius < best_radius:
                best_radius = radius
                best_fi = fi
                best_fr = fr

                # if is first improvement, apply the swap now
                if is_first_improvement:
                    break

        # if didn't improve
        if best_radius >= current_radius:
            return False

        # O(mn)
        self.apply_swap(best_fi, best_fr)

        return True

    def fast_vertex_substitution(self, is_first_improvement: bool) -> Solution:
        """
        Alpha Fast Vertex Substitution (ANPCP) local search heuristic.

        Time O(mpn) * C,
        where C is the number of attempts to keep improving S.
        """
        moves = 0
        while self.try_improve(is_first_improvement):
            moves += 1

        self.solution.moves = moves

        return self.solution

    def tabu_try_improve(self, best_global: int) -> bool:
        current_radius = self.solution.get_obj_func()

        best_local = math.inf
        best_fi = best_fr = -1

        ## O(mpn)
        # O(m - p) ~= O(m) since m > p
        for fi in self.solution.closed_facilities:
            fi_distance = self.instance.get_distance(
                self.solution.critical_allocation.user, fi
            )

            if fi_distance >= current_radius:
                continue

            # O(pn)
            best_move = self.move(fi)
            fr = best_move.index
            radius = best_move.radius

            # if is tabu and aspiration criteria not met
            if is_tabu(fr) and radius >= best_global:
                continue

            # if not tabu or aspiration criteria met
            if radius < best_local:
                best_local = radius
                best_fi = fi
                best_fr = fr

        # mark attribute as tabu

        # O(mn)
        self.apply_swap(best_fi, best_fr)

        return self.solution.get_obj_func() < current_radius

    def tabu_search(self, tenure: int, iters: int) -> Solution:
        best_so_far = self.solution.get_obj_func()

        i = 0
        while i < iters:
            # TODO: add parameter to support tabu moves
            self.tabu_try_improve(best_so_far)

            best_so_far = min(best_so_far, self.solution.get_obj_func())
            i += 1

        return self.solution

    def grasp(self, iters: int, beta: float = 0, time_limit: float = -1) -> Solution:
        """
        Applies the GRASP metaheuristic to the current solver,
        and stops when either `iters` or `time_limit` is reached.

        `iters`: Number of consecutive iterations without improvement to stop.

        `beta`: Value between 0 and 1 for the RCL in the constructive heuristic.
        Use -1 to use a random value in each iteration.

        `time_limit`: Time limit in seconds to stop. Use -1 for no limit.
        """
        if time_limit == -1:
            time_limit = math.inf

        best_solution = None
        best_radius = current_radius = math.inf

        total_time = moves = 0

        last_imp = i = iwi = 0
        while iwi < iters and total_time < time_limit:
            self.init_solution()

            beta_used = random.random() if beta == -1 else beta

            start = timeit.default_timer()

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
        self.solution.last_improvement = last_imp

        return self.solution

    def _grasp_iters_detailed(self, max_iters: int, beta: float) -> pd.DataFrame:
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


def generate_solvers(
    instances: Sequence[Instance],
    p_percentages: Sequence[float],
    alpha_values: Sequence[int],
) -> List[Solver]:
    return [
        Solver(instance, int(instance.m * p), alpha)
        for instance in instances
        for p in p_percentages
        for alpha in alpha_values
    ]
