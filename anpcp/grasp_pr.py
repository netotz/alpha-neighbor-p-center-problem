from enum import Enum
import itertools
import math
import os
import re
import timeit

import click
import numpy as np
import pandas as pd

from models.instance import Instance
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
    def __init__(self) -> None:
        self.did_improveds: list[bool] = []
        self.best_solution: SolutionSet | None = None
        self.time: float = 0

    def count_improvements(self) -> int:
        return sum(1 if i else 0 for i in self.did_improveds)


class PathRelinkingStats(BaseStats):
    def __init__(self) -> None:
        self.relinkeds: list[SolutionSet] = []
        self.ls_time: float = 0
        self.ls_did_improveds: list[bool] = []

        super().__init__()

    def count_paths(self) -> int:
        return len(self.relinkeds)

    def count_ls_improvements(self) -> int:
        return sum(1 if i else 0 for i in self.ls_did_improveds)


class PostOptimizationStats(BaseStats):
    def __init__(self) -> None:
        self.pr_stats: list[PathRelinkingStats] = []
        self.total_time: float = 0
        self.grasp_best_solution: SolutionSet | None = None

        super().__init__()

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
    def __init__(
        self,
        instance: Instance,
        p: int,
        alpha: int,
        with_random_solution=False,
        is_first_improvement=True,
        seed: int | None = None,
    ):
        self.pr_algorithm: LocalSearchAlgorithm | None = None
        self.current_pr_stats: PathRelinkingStats | None = None
        self.po_stats = PostOptimizationStats()

        super().__init__(
            instance, p, alpha, with_random_solution, is_first_improvement, seed
        )

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
        # O(p)
        best_solution = min(starting, target).copy()
        # O(p)
        original_best = best_solution.copy()

        # O(p), worst case if both solutions are completely different
        candidates_out = set(starting.open_facilities - target.open_facilities)
        # O(p)
        candidates_in = set(target.open_facilities - starting.open_facilities)

        # O(p)
        relinked = starting.copy()
        self.path_relinking_state.start(candidates_out, candidates_in)

        best_move_getter = self.__get_pr_method()

        ## O(mpn + p**3 n + mp**2 n + 2p) ~= O(mp**2 n + p**3 n)
        # O(p)
        while self.path_relinking_state.are_there_candidates():
            # O(mn)
            self.replace_solution(relinked)

            # O(mn + p**2 n)
            best_move = best_move_getter()
            self.path_relinking_state.update_candidates(best_move.fi, best_move.fr)

            # O(p)
            relinked = SolutionSet.from_solution(self.solution)
            self.current_pr_stats.relinkeds.append(relinked)

            self.path_relinking_state.pause()
            start_ls = timeit.default_timer()
            # there's no guarantee that relinked solution is local optimum
            # O(mpn)
            local_optimum = self.fast_vertex_substitution()
            self.current_pr_stats.ls_time += timeit.default_timer() - start_ls
            self.path_relinking_state.resume()

            self.current_pr_stats.ls_did_improveds.append(
                local_optimum.obj_func < relinked.obj_func
            )

            self.current_pr_stats.did_improveds.append(
                local_optimum.obj_func < original_best.obj_func
            )

            if local_optimum.obj_func < best_solution.obj_func:
                # O(p)
                best_solution = SolutionSet.from_solution(local_optimum)

        self.path_relinking_state.end()

        # O(p)
        self.current_pr_stats.best_solution = best_solution.copy()

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
        # O(p)
        best_solution = pool.get_best().copy()
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
        # O(p)
        self.po_stats.best_solution = best_solution.copy()

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

    solvers = get_solvers(name, variations, p_percents, alpha_values)

    for solver in solvers:
        print(
            f"\tCurrent: {solver.instance.name}, p = {solver.p}, alpha = {solver.alpha} ..."
        )

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
        "algorithm",
        #
        "best_grasp",
        "best_po",
        "best_diff",
        #
        "po_imps",
        "pr_avg_imps",
        "pr_ls_avg_imps",
        #
        "time_total",
        "time_po",
        "time_po_%",
        #
        "time_pr_avg",
        "time_pr_ls_%_avg",
    ]
    datalist = [
        [
            name,
            prs.instance.index,
            prs.p,
            prs.alpha,
            prs.pr_algorithm,
            #
            prs.po_stats.grasp_best_solution.obj_func,
            prs.po_stats.best_solution.obj_func,
            prs.po_stats.get_obj_func_diff(),
            #
            prs.po_stats.count_improvements(),
            prs.po_stats.get_pr_imps_mean(),
            prs.po_stats.get_pr_ls_imps_mean(),
            #
            prs.solution.time,
            prs.po_stats.time,
            prs.po_stats.get_times_diff(),
            #
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


def get_filenames() -> list[str]:
    """
    Searches the directory `FINAL_PATH` and returns a list of
    the filenames of the experiment results.
    """
    EXTENSION = ".pkl"

    filenames = [
        # remove prefix and extension from filename
        filename[len(PREFIX) :].split(".")[0]
        for filename in os.listdir(PR_PATH)
        # ignore 'solver_' and .tex files
        if filename.startswith(PREFIX) and filename.endswith(EXTENSION)
    ]
    # sort names by number of nodes
    filenames.sort(key=lambda n: int(re.findall(r"\d+", n)[0]))

    return filenames


if __name__ == "__main__":
    print("Running...")
    __run()
    print("Finished.")
