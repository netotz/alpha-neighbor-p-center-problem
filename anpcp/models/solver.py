from copy import deepcopy
from enum import Enum
import itertools
from typing import Sequence
import heapq
import math
import timeit

import numpy as np
import pandas as pd

from .elite_pool import ElitePool
from .instance import Instance
from .reactive_beta import ReactiveBeta
from .solution import Solution
from .solution_set import SolutionSet
from .tabu_structures import TabuRecency
from .wrappers import (
    AllocatedFacility,
    BestMove,
    LargestTwo,
    LocalSearchState,
    MinMaxAvg,
    MovedFacility,
)


class NotAllocatedError(Exception):
    pass


class LocalSearchAlgorithm(Enum):
    GI = 0
    """
    Greedy Interchange
    """
    AFVS = 1
    """
    Alpha Fast Vertex Substitution
    """


class Solver:
    def __init__(
        self,
        instance: Instance,
        p: int,
        alpha: int,
        with_random_solution=False,
        is_first_improvement=True,
        seed: int | None = None,
    ):
        self.instance = instance
        self.p = p
        self.alpha = alpha
        self.with_random_solution = with_random_solution
        self.__set_alpha_range()

        self.seed = seed
        self.rng = np.random.default_rng(seed)

        self.allocations = np.zeros(
            (self.instance.n, self.instance.m),
            np.ubyte,
        )
        self.critical_allocation: AllocatedFacility | None = None

        self.__init_solution()
        if self.with_random_solution:
            self.randomize_solution()
        else:
            self.solution.closed_facilities = self.instance.facilities_indexes.copy()

        self.history: list[Solution] = []
        self.local_search = LocalSearchState(
            self.solution.open_facilities,
            self.solution.closed_facilities,
            is_first_improvement,
        )

    def __repr__(self) -> str:
        return f"{Solver.__name__}(I={self.instance}, p={self.p}, a={self.alpha})"

    def __set_alpha_range(self) -> None:
        self.alpha_range = set(range(1, self.alpha + 2))

    def __init_solution(self):
        self.solution = Solution()

    def randomize_solution(self) -> Solution:
        # O(m + p)
        self.solution.open_facilities = set(
            self.rng.choice(
                np.fromiter(self.instance.facilities_indexes, int),
                self.p,
                replace=False,
                shuffle=False,
            )
        )
        # O(m)
        self.solution.closed_facilities = (
            self.instance.facilities_indexes - self.solution.open_facilities
        )

        # O(mn)
        self.update_solution()

        return self.solution

    def replace_solution(self, set: SolutionSet) -> None:
        """
        Replaces `self.solution` using the data contained in `set` of type `SolutionSet`.

        Time O(mn)
        """
        self.__init_solution()
        self.solution.open_facilities = set.open_facilities.copy()
        # O(m)
        self.solution.closed_facilities = (
            self.instance.facilities_indexes - self.solution.open_facilities
        )
        # O(mn)
        self.update_solution()

    @classmethod
    def from_solver(cls, solver: "Solver"):
        """
        Returns a shallow copy of `solver`.
        This method was created to get an instance of a derived solver,
        like `GraspFinalSolver`.
        """
        return cls(solver.instance, solver.p, solver.alpha)

    def get_users_indexes(self) -> set[int]:
        return self.instance.users_indexes

    def reallocate_user(self, user: int) -> None:
        """
        Reallocates a user to its alpha-neighbors.

        Time: O(m)
        """
        # deallocate user from all facilities
        # O(m)
        self.allocations[user, :] = 0

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

            self.allocations[user, facility] = k

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

    def get_kth_closest(self, user: int, kth: int) -> AllocatedFacility:
        """
        Gets the `kth` closest facility from `user` with its distance.

        Raises `NotAllocatedError` if there's no `kth` in allocations matrix.

        To get the alpha-neighbors of `user`, see `get_alpha_neighbors`.

        Time: O(p)
        """
        # O(p)
        for facility in self.solution.open_facilities:
            if self.allocations[user, facility] == kth:
                return AllocatedFacility(
                    facility,
                    user,
                    self.instance.get_distance(user, facility),
                )

        raise NotAllocatedError

    def get_alpha_neighbors(self, user: int) -> dict[int, AllocatedFacility]:
        """
        Gets the closest facilities from `user` up to its center (including it) with their distances.

        Returns a dictionary with the k-th position as key and an `AllocatedFacility` object as value.

        To get only one facility, see `get_kth_closest`.

        Time: O(p)
        """
        alpha_neighbors: dict[int, AllocatedFacility] = dict()

        # O(p)
        for facility in self.solution.open_facilities:
            k = self.allocations[user, facility]

            # if no stored allocation
            if k == 0:
                continue

            alpha_neighbors[k] = AllocatedFacility(
                facility,
                user,
                self.instance.get_distance(user, facility),
            )

            # when all kth positions are found
            if len(alpha_neighbors) == self.alpha + 1:
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
        self.critical_allocation = self.eval_obj_func()
        self.solution.obj_func = self.critical_allocation.distance

    def update_solution(self) -> None:
        """
        Time O(mn)
        """
        # O(mn)
        self.allocate_all()
        # O(pn)
        self.update_obj_func()

    def apply_swap(self, facility_in, facility_out) -> None:
        """
        Inserts `facility_in` into solution, removes `facility_out` from it,
        and updates allocations and objective function.

        Time O(mn + pn) ~= O(mn) since m > p
        """
        self.solution.swap(facility_in, facility_out)

        if not self.local_search.is_path_relinking:
            self.local_search.update_candidates(
                self.solution.open_facilities,
                self.solution.closed_facilities,
            )
        # update for Path Relinking is made in its method

        # O(mn)
        self.update_solution()

    def reset_alpha(self, new_alpha: int) -> None:
        """
        Resets this solver with `new_alpha` as the alpha parameter,
        keeping the same solution.
        """
        self.alpha = new_alpha
        self.__set_alpha_range()
        # O(mn)
        self.update_solution()

    def get_users_per_center_stats(self):
        min_users = math.inf
        max_users = -math.inf
        users_sum = 0

        for center in self.solution.open_facilities:
            users = sum(
                self.allocations[user, center] == self.alpha
                for user in range(self.instance.n)
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
        # O(m)
        last_inserted: int = self.rng.choice(
            np.fromiter(solution.closed_facilities, int), 1
        )[0]
        solution.insert(last_inserted)

        ## O(mp)
        # O(p)
        while len(solution.open_facilities) < self.p:
            facilities: list[MovedFacility] = []
            min_cost = math.inf
            max_cost = -math.inf

            # O(m)
            for fi in solution.closed_facilities:
                s_dists[fi] = min(
                    s_dists[fi], self.instance.facilities_distances[fi, last_inserted]
                )
                facility = MovedFacility(fi, s_dists[fi])

                max_cost = max(max_cost, s_dists[fi])
                min_cost = min(min_cost, s_dists[fi])

                facilities.append(facility)

            threshold = max_cost - beta * (max_cost - min_cost)
            # O(m)
            last_inserted = self.rng.choice(
                [f.index for f in facilities if f.radius >= threshold], 1
            )[0]
            solution.insert(last_inserted)

        self.solution = solution
        # update for local search
        self.local_search.update_candidates(
            self.solution.open_facilities,
            self.solution.closed_facilities,
        )

        # O(mn)
        self.update_solution()

        return self.solution

    def interchange(self) -> Solution:
        """
        Greedy Interchange, checks every possible swap.

        Time O(m**2 pn)
        """
        best_radius = current_radius = self.solution.obj_func
        best_fi = best_fr = -1

        moves = 0
        is_improved = True
        while is_improved:
            ## O(m**2 pn)
            # O(m - p) ~= O(m)
            for fi in self.solution.closed_facilities:
                fi_distance = self.instance.get_distance(
                    self.critical_allocation.user, fi
                )

                if fi_distance >= current_radius:
                    continue

                ## O(mpn)
                # O(p)
                for fr in self.solution.open_facilities:
                    # O(mn)
                    self.apply_swap(fi, fr)

                    if self.solution.obj_func < best_radius:
                        best_radius = self.solution.obj_func
                        best_fi = fi
                        best_fr = fr

                        if self.local_search.is_first_improvement:
                            break

                    # if it's best improvement, "restore" base solution
                    # by reverting the swap
                    self.solution.swap(fr, fi)

                is_improved = best_radius < current_radius
                if is_improved and self.local_search.is_first_improvement:
                    break
                # if solution hasn't improved in FI, or strategy is BI,
                # keep searching (next fi)

            is_improved = best_radius < current_radius
            # apply the move
            if is_improved:
                if self.local_search.is_first_improvement:
                    current_radius = best_radius
                    # current solution is already best,
                    # because it's the last one updated
                    continue

                # O(mn)
                self.apply_swap(best_fi, best_fr)
                moves += 1

                current_radius = best_radius = self.solution.obj_func

        # if S didn't improve,
        # it must be updated still because the last swap (the "restored")
        # doesn't update it
        self.update_solution()
        self.solution.moves = moves

        return self.solution

    def interchange_relinking(self) -> BestMove:
        """
        Greedy Interchange for Path Relinking, checks every possible swap.

        Time O(mp**2 n)
        """
        best_radius = math.inf
        best_fi = best_fr = -1

        ## O(mp**2 n)
        # O(p)
        for fi in self.local_search.candidates_in:
            ## O(mpn)
            # O(p)
            for fr in self.local_search.candidates_out:
                # O(mn)
                self.apply_swap(fi, fr)

                if self.solution.obj_func < best_radius:
                    best_radius = self.solution.obj_func
                    best_fi = fi
                    best_fr = fr

                # "restore" base solution by reverting the swap
                self.solution.swap(fr, fi)

        # O(mn)
        self.apply_swap(best_fi, best_fr)

        return BestMove(best_fi, best_fr, self.solution.obj_func)

    def __get_best_fr(
        self,
        best_radius: int,
        lost_neighbors: dict[int, int],
        largest_two: LargestTwo,
    ) -> MovedFacility:
        """
        Returns the best facility to remove (fr) given the parameters.

        Time O(p)
        """
        min_fr = -1
        min_radius = math.inf

        # O(p)
        for fr in lost_neighbors.keys():
            # only consider facilities that are in Path Relinking subset
            if (
                self.local_search.is_path_relinking
                and fr not in self.local_search.candidates_out
            ):
                continue

            current_radius = max(
                best_radius,
                lost_neighbors[fr],
                largest_two.second.radius
                if fr == largest_two.first.index
                else largest_two.first.radius,
            )

            if current_radius < min_radius:
                min_radius = current_radius
                min_fr = fr

        return MovedFacility(min_fr, min_radius)

    def get_facility_out(self, facility_in: int) -> MovedFacility:
        """
        Determines the best facility to remove if `facility_in` was inserted,
        and the objective function resulting from the swap.

        Time O(pn + 4p) ~= O(pn)
        """
        # best objective function so far
        best_radius = 0

        # even if it's Path Relinking, all open facilities must be considered
        # because the a-neighbors of any user could be outside the candidates_out
        # O(p)
        same_neighbors = {fr: 0 for fr in self.solution.open_facilities}
        # O(p)
        lost_neighbors = dict(same_neighbors)

        ## O(n(p + a)) ~= O(pn) since p > a, a ~= 1
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
                fj = neighbor.index

                # alphath is irrelevant if user is attracted to fi
                if is_attracted and fj == alphath.index:
                    continue

                lost_neighbors[fj] = max(lost_neighbors[fj], lost_arg)
                same_neighbors[fj] = max(same_neighbors[fj], same_arg)

        # O(p)
        largest_two = LargestTwo(same_neighbors)
        # O(p)
        return self.__get_best_fr(best_radius, lost_neighbors, largest_two)

    def does_break_critical(self, facility_in) -> bool:
        """
        Returns `True` if `facility_in` would break the critical allocation of
        the current solution.
        Otherwise returns `False`.
        """
        fi_distance = self.instance.get_distance(
            self.critical_allocation.user, facility_in
        )

        return fi_distance < self.solution.obj_func

    def get_best_move(self) -> BestMove:
        """
        Returns the best move in the A-FVS algorithm.

        Time O(mpn)
        """
        # best radius starts as current radius
        best_radius = self.solution.obj_func
        best_fi = best_fr = -1

        ## O(mpn)
        # O(m - p) ~= O(m), m > p
        for fi in self.solution.closed_facilities:
            if not self.does_break_critical(fi):
                continue

            # O(pn)
            facility_out = self.get_facility_out(fi)

            # if move improves x(S)
            if facility_out.radius < best_radius:
                best_radius = facility_out.radius
                best_fi = fi
                best_fr = facility_out.index

                # if is first improvement, apply the swap now
                if self.local_search.is_first_improvement:
                    break

        return BestMove(best_fi, best_fr, best_radius)

    def get_best_move_relinking(self) -> BestMove:
        """
        Returns the best move using A-FVS for Path Relinking,
        meaning it allows worse moves.

        Time O(p**2 n)
        """
        # best radius starts as infinity
        best_radius = math.inf
        best_fi = best_fr = -1

        ## O(p**2 n)
        # O(p)
        for fi in self.local_search.candidates_in:
            # O(pn)
            facility_out = self.get_facility_out(fi)

            # if move improves current x(S)
            if facility_out.radius < best_radius:
                best_radius = facility_out.radius
                best_fi = fi
                best_fr = facility_out.index

        return BestMove(best_fi, best_fr, best_radius)

    def try_improve(self) -> bool:
        """
        Returns `True` if x(S) was improved by searching for the best facility to insert
        and the best one to remove.
        If no possible move improves current S, returns `False`.

        Time O(mpn + mn) ~= O(mpn)
        """
        # O(mpn)
        best_move = self.get_best_move()

        # if didn't improve
        if best_move.radius >= self.solution.obj_func:
            return False

        # O(mn)
        self.apply_swap(best_move.fi, best_move.fr)

        return True

    def try_improve_relinking(self) -> BestMove:
        """
        Tries to improve S by applying Path Relinking, using ANPCP.

        Time O(mn + p**2 n)
        """
        # O(p**2 n)
        best_move = self.get_best_move_relinking()

        # O(mn)
        self.apply_swap(best_move.fi, best_move.fr)

        return best_move

    def fast_vertex_substitution(self) -> Solution:
        """
        Alpha Fast Vertex Substitution (ANPCP) local search heuristic.

        Time O(mpn)*C,
        where C is the number of attempts to keep improving S.
        """
        moves = 0
        while self.try_improve():
            moves += 1

        self.solution.moves = moves

        return self.solution

    def tabu_try_improve(self, best_global: int, recency: TabuRecency) -> bool:
        current_radius = self.solution.obj_func

        best_local = math.inf
        best_fi = best_fr = -1

        ## O(mpn)
        # O(m - p) ~= O(m) since m > p
        for fi in self.solution.closed_facilities:
            if not self.does_break_critical(fi):
                continue

            # O(pn)
            best_move = self.get_facility_out(fi)
            fr = best_move.index
            radius = best_move.radius

            # if is tabu and aspiration criteria not met
            if recency.is_tabu(fr) and radius >= best_global:
                continue

            # if not tabu or aspiration criteria met
            if radius < best_local:
                best_local = radius
                best_fi = fi
                best_fr = fr

        # if no swaps occured
        if best_local == math.inf:
            return False

        # O(mn)
        self.apply_swap(best_fi, best_fr)
        # mark fi as tabu
        recency.mark(best_fi)

        return self.solution.obj_func < current_radius

    def tabu_search(self, tenure: int, iters: int) -> Solution:
        best_so_far = self.solution.obj_func

        # TODO: calculate memory size from tenure
        recency = TabuRecency(tenure)

        i = 0
        while i < iters:
            self.tabu_try_improve(best_so_far, recency)

            best_so_far = min(best_so_far, self.solution.obj_func)
            i += 1

        return self.solution

    def path_relink(
        self,
        starting: SolutionSet,
        target: SolutionSet,
        algorithm: LocalSearchAlgorithm,
    ) -> SolutionSet:
        """
        Performs a Path Relinking between `starting` and `target` solutions.
        Returns the best of `starting`, `target`, or best relinked found.

        Time O(mnp + p**3 n)
        """
        # O(p), worst case if both solutions are completely different
        candidates_out = starting.open_facilities - target.open_facilities
        # O(p)
        candidates_in = target.open_facilities - starting.open_facilities

        # O(mn)
        self.replace_solution(starting)
        self.local_search.start_path_relinking(candidates_out, candidates_in)

        minheap: list[SolutionSet] = [min(starting, target)]

        methods = {
            LocalSearchAlgorithm.GI: self.interchange_relinking,
            LocalSearchAlgorithm.AFVS: self.try_improve_relinking,
        }
        best_move_getter = methods[algorithm]

        ## O(mnp + p**3 n + 2p + p log p) ~= O(mnp + p**3 n)
        # O(p)
        while self.local_search.are_there_candidates():
            # O(mn + p**2 n)
            best_move = best_move_getter()

            self.local_search.remove_applied_candidates(best_move.fi, best_move.fr)

            # O(p)
            current = SolutionSet.from_solution(self.solution)

            if current < starting or current < target:
                # O(log p)
                heapq.heappush(
                    minheap,
                    current,
                )

        self.local_search.end_path_relinking(
            self.solution.open_facilities, self.solution.closed_facilities
        )

        return min(minheap[0], starting, target)

    def grasp(
        self,
        iters: int,
        beta_period: int = 1,
        time_limit: float = math.inf,
        pool_limit: int = 1,
    ) -> Solution:
        """
        Applies the GRASP metaheuristic to the current solver,
        and stops when either `iters` or `time_limit` is reached.

        `iters`: Number of consecutive iterations without improvement to stop.

        `beta_period`: Period of iterations to update the probabilities of beta values.

        `time_limit`: Time limit in seconds to stop.

        `pool_limit`: Max amount of solutions in the elites pool.
        """
        start = timeit.default_timer()

        reactive = ReactiveBeta(seed=self.seed)
        pool = ElitePool(pool_limit)

        best_solution: SolutionSet | None = None

        total_time = moves = 0
        last_imp = i = iwi = 0

        while iwi < iters and total_time < time_limit:
            self.__init_solution()

            beta_used = reactive.choose()

            # O(mp)
            self.construct(beta_used)
            # O(mpn)
            self.fast_vertex_substitution()

            # O(p)
            current_solution = SolutionSet.from_solution(self.solution)
            # O(log l)
            pool.try_add(current_solution)

            reactive.increment(beta_used, self.solution.obj_func)

            if best_solution is None or pool.get_best() < best_solution:
                best_solution = pool.get_best()
                moves += 1

                iwi = 0
                last_imp = i
            else:
                iwi += 1

            # don't update reactive beta in first iteration
            if i > 0 and i % beta_period == 0:
                reactive.update(best_solution.obj_func)

            i += 1

        # O(?)
        self.post_optimize(pool)

        total_time = timeit.default_timer() - start

        self.solution.time = total_time
        self.solution.moves = moves
        self.solution.last_improvement = last_imp

        return self.solution

    def post_optimize(self, pool: ElitePool) -> Solution:
        """
        Runs Path Relinking for each pair of solutions in `pool` and sets the best found
        as the current solution of this solver.
        """
        best_solution = pool.get_best()

        # O(l**2)
        for starting, target in itertools.combinations(pool.iter_solutions(), 2):
            # O(mnp + p**3 n)
            relinked = self.path_relink(starting, target, LocalSearchAlgorithm.AFVS)

            best_solution = min(relinked, best_solution)

        # O(mn)
        self.replace_solution(best_solution)

        return self.solution


def generate_solvers(
    instances: Sequence[Instance],
    p_percentages: Sequence[float],
    alpha_values: Sequence[int],
) -> list[Solver]:
    return [
        Solver(instance, int(instance.m * p), alpha)
        for instance in instances
        for p in p_percentages
        for alpha in alpha_values
    ]
