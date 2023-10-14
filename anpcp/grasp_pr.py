from enum import Enum
import itertools
import math
import os
import timeit

import click
import numpy as np
import pandas as pd

from models.elite_pool import ElitePool
from models.reactive_beta import ReactiveBeta
from models.solution import Solution
from models.solution_set import SolutionSet
from models.solver import Solver
from models.solver_io import write_solver_pickle
from utils import get_solvers


class LocalSearchAlgorithm(Enum):
    GI = 0
    """
    Greedy Interchange
    """
    AFVS = 1
    """
    Alpha Fast Vertex Substitution
    """


class BaseStats:
    did_improveds: list[bool] = []
    best_solution: SolutionSet
    time: float = 0

    def count_improvements(self) -> int:
        return len(i for i in self.did_improveds if i)


class PathRelinkingStats(BaseStats):
    relinkeds: list[SolutionSet] = []
    ls_time: float = 0
    ls_did_improveds: list[bool] = []

    def count_paths(self) -> int:
        return len(self.relinkeds)

    def count_ls_improvements(self) -> int:
        return len(i for i in self.ls_did_improveds if i)


class PostOptimizationStats(BaseStats):
    pr_stats: list[PathRelinkingStats] = []
    total_time: float = 0
    grasp_best_solution: SolutionSet | None = None

    def get_pr_imps_mean(self) -> float:
        return np.array([p.count_improvements() for p in self.pr_stats]).mean()

    def get_pr_ls_imps_mean(self) -> float:
        return np.array([p.count_ls_improvements() for p in self.pr_stats]).mean()

    def get_pr_times_mean(self) -> float:
        return np.array([p.time for p in self.pr_stats]).mean()

    def get_pr_ls_times_percents_mean(self) -> float:
        times = np.array([p.time for p in self.pr_stats])
        ls_times = np.array([p.ls_time for p in self.pr_stats])

        percents = (100 * ls_times) / times

        return percents.mean()

    def get_obj_func_diff(self) -> float:
        return (
            100
            * abs(self.best_solution.obj_func - self.grasp_best_solution.obj_func)
            / self.grasp_best_solution.obj_func
        )

    def get_times_diff(self) -> float:
        return (100 * self.time) / self.total_time


class ExperimentalSolver(Solver):
    pr_algorithm: LocalSearchAlgorithm
    current_pr_stats: PathRelinkingStats | None
    po_stats = PostOptimizationStats()

    def __get_pr_method(self):
        methods = {
            LocalSearchAlgorithm.GI: self.interchange_relinking,
            LocalSearchAlgorithm.AFVS: self.try_improve_relinking,
        }

        return methods[self.pr_algorithm]

    def path_relink(self, starting: SolutionSet, target: SolutionSet) -> SolutionSet:
        """
        Performs a Path Relinking between `starting` and `target` solutions.
        Returns the best of `starting`, `target`, or best relinked found.

        Time O(mp**2 n + p**3 n)
        """
        best_solution = min(starting, target)
        # O(p)
        original_best = best_solution.copy()

        # O(p), worst case if both solutions are completely different
        candidates_out = set(starting.open_facilities - target.open_facilities)
        # O(p)
        candidates_in = set(target.open_facilities - starting.open_facilities)

        # O(mn)
        self.replace_solution(starting)

        self.path_relinking_state.start(candidates_out, candidates_in)

        best_move_getter = self.__get_pr_method()

        ## O(mpn + p**3 n + mp**2 n + 2p) ~= O(mp**2 n + p**3 n)
        # O(p)
        while self.path_relinking_state.are_there_candidates():
            # O(mn + p**2 n)
            best_move = best_move_getter()
            self.path_relinking_state.update_candidates(best_move.fi, best_move.fr)

            prev_of = self.solution.obj_func

            self.path_relinking_state.pause()
            start_ls = timeit.default_timer()
            # there's no guarantee that relinked solution is local optimum
            # O(mpn)
            self.fast_vertex_substitution()
            self.current_pr_stats.ls_time += timeit.default_timer() - start_ls
            self.path_relinking_state.resume()

            ls_of = self.solution.obj_func
            self.current_pr_stats.ls_did_improveds.append(ls_of < prev_of)

            # O(p)
            relinked = SolutionSet.from_solution(self.solution)

            self.current_pr_stats.relinkeds.append(relinked)
            self.current_pr_stats.did_improveds.append(relinked < original_best)

            best_solution = min(best_solution, relinked)

        self.path_relinking_state.end()

        self.current_pr_stats.best_solution = best_solution

        return best_solution

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
            self.init_solution()

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

        self.po_stats.grasp_best_solution = best_solution

        start_po = timeit.default_timer()
        # O(?)
        self.post_optimize(pool)
        self.po_stats.time = timeit.default_timer() - start_po

        total_time = timeit.default_timer() - start
        self.po_stats.total_time = total_time

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
        # O(p)
        grasp_best = best_solution.copy()

        # O(l**2)
        for starting, target in itertools.combinations(pool.iter_solutions(), 2):
            self.current_pr_stats = PathRelinkingStats()
            start_pr = timeit.default_timer()

            # O(mnp + p**3 n)
            best_relinked = self.path_relink(starting, target)

            self.current_pr_stats.time = timeit.default_timer() - start_pr

            self.po_stats.pr_stats.append(self.current_pr_stats)
            self.po_stats.did_improveds.append(best_relinked < grasp_best)

            best_solution = min(best_solution, best_relinked)

        # O(mn)
        self.replace_solution(best_solution)
        self.po_stats.best_solution = best_solution

        return self.solution


PR_PATH = os.path.join("nb_results", "pr")
PREFIX = "pr_"


@click.command()
@click.option(
    "-n",
    "--name",
    required=True,
    help="Instance names, without extension or index.",
)
@click.option(
    "-v",
    "--variations",
    type=int,
    default=10,
    show_default=True,
    help="Maximum number of variations of the base instance (--name) to run.",
)
@click.option(
    "-p",
    "--p-percents",
    multiple=True,
    type=float,
    default=[0.05, 0.1, 0.15],
    show_default=True,
    help="Decimal percentages for p where 1 = 100%.",
)
@click.option(
    "-a",
    "--alpha-values",
    multiple=True,
    type=int,
    default=[2, 3],
    show_default=True,
    help="Values for alpha.",
)
@click.option(
    "-i",
    "--iters",
    type=int,
    default=100,
    show_default=True,
    help="Consecutive iterations without improvement to stop.",
)
@click.option(
    "-b",
    "--beta-period",
    type=int,
    default=25,
    show_default=True,
    help="Period to update the reactive beta parameter.",
)
@click.option(
    "-l",
    "--pool-limit",
    type=int,
    default=20,
    show_default=True,
    help="Limit size of elite pool.",
)
@click.option(
    "-t",
    "--time",
    type=float,
    default=1800,
    show_default=True,
    help="Time limit in seconds before stopping. Use -1 for no limit.",
)
def __run(
    name: str,
    variations: int,
    p_percents: list[float],
    alpha_values: list[int],
    iters: int,
    beta_period: int,
    pool_limit: int,
    time: float,
):
    pr_solvers: list[ExperimentalSolver] = []

    for solver in get_solvers(name, variations, p_percents, alpha_values):
        print(
            f"\tCurrent: {solver.instance.name}, p = {solver.p}, alpha = {solver.alpha} ..."
        )

        row = [name, solver.instance.index, solver.p, solver.alpha]

        for pr_algorithm in [LocalSearchAlgorithm.GI, LocalSearchAlgorithm.AFVS]:
            print(f"\t\tPath Relinking algorithm: {pr_algorithm} ...")

            prs = ExperimentalSolver.from_solver(solver)
            prs.pr_algorithm = pr_algorithm

            write_solver_pickle(prs, PR_PATH)

            prs.grasp(iters, beta_period, time, pool_limit)

            pr_solvers.append(prs)

    headers = [
        "instance",
        "i",
        "p",
        "alpha",
        "best_grasp",
        "best_po",
        "best_diff",
        "po_imps",
        "pr_avg_imps",
        "pr_ls_avg_imps",
        "time_total",
        "time_po",
        "time_po_%",
        "time_pr_avg",
        "time_pr_ls_%_avg",
    ]
    datalist = [
        [
            name,
            prs.instance.index,
            prs.p,
            prs.alpha,
            prs.po_stats.grasp_best_solution.obj_func,
            prs.po_stats.best_solution.obj_func,
            prs.po_stats.get_obj_func_diff(),
            prs.po_stats.count_improvements(),
            prs.po_stats.get_pr_imps_mean(),
            prs.po_stats.get_pr_ls_imps_mean(),
            prs.solution.time,
            prs.po_stats.time,
            prs.po_stats.get_times_diff(),
            prs.po_stats.get_pr_times_mean(),
            prs.po_stats.get_pr_ls_times_percents_mean(),
        ]
        for prs in pr_solvers
    ]
    results = pd.DataFrame(datalist, columns=headers)

    filepath = os.path.join(PR_PATH, f"{PREFIX}{name}.pkl")
    results.to_pickle(filepath)


def read_results(instance_name: str) -> pd.DataFrame:
    filepath = os.path.join(PR_PATH, f"{PREFIX}{instance_name}.pkl")

    return pd.read_pickle(filepath)


if __name__ == "__main__":
    print("Running...")
    __run()
    print("Finished.")
