from copy import deepcopy
import math
import os
import random
import re
import timeit

import pandas as pd
import click

from models.solver_io import write_solver_pickle
from models.solver import Solver
from utils import get_solvers, DATA_PATH


FINAL_PATH = os.path.join("nb_results", "grasp", "final")


class GraspFinalSolver(Solver):
    def _grasp_final(self, iters: int, beta: float, time_limit: float = -1):
        """
        Modified method for final experiments of GRASP.
        """
        if time_limit == -1:
            time_limit = math.inf

        best_solution = None
        best_rgd_of = best_afvs_of = math.inf

        # relative improvements by local search AFVS
        min_afvs_improvement = math.inf
        max_afvs_improvement = -math.inf
        afvs_improvements_sum = 0

        total_time = moves = 0

        last_imp = i = iwi = 0
        while iwi < iters and total_time < time_limit:
            self.init_solution()

            beta_used = random.random() if beta == -1 else beta

            start = timeit.default_timer()
            self.construct(beta_used)
            total_time += timeit.default_timer() - start

            rgd_of = self.solution.get_obj_func()
            best_rgd_of = min(best_rgd_of, rgd_of)

            start = timeit.default_timer()
            self.fast_vertex_substitution(True)
            total_time += timeit.default_timer() - start

            afvs_of = self.solution.get_obj_func()
            afvs_improvement = 100 * abs(afvs_of - rgd_of) / rgd_of
            min_afvs_improvement = min(min_afvs_improvement, afvs_improvement)
            max_afvs_improvement = max(max_afvs_improvement, afvs_improvement)
            afvs_improvements_sum += afvs_improvement

            if best_solution is None or afvs_of < best_afvs_of:
                best_solution = deepcopy(self.solution)
                best_afvs_of = afvs_of
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

        avg_afvs_improvement = afvs_improvements_sum / i
        best_rgd_diff = 100 * abs(best_afvs_of - best_rgd_of) / best_rgd_of

        return (
            best_rgd_of,
            best_afvs_of,
            best_rgd_diff,
            min_afvs_improvement,
            max_afvs_improvement,
            avg_afvs_improvement,
        )


# tentative instances for final experiment
names = [
    "pr439_293_146",
    "rat575_384_191",
    "rat783_522_261",
    "dsj1000_667_333",
    "rl1323_882_441",
    "rl1889_1260_629",
]


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
    "--beta",
    type=float,
    default=0.2,
    show_default=True,
    help="Value for the beta parameter.",
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
    beta: float,
    time: float,
):
    datalist = []

    solvers: list[Solver] = get_solvers(name, variations, p_percents, alpha_values)

    for solver in solvers:
        print(
            f"\tCurrent: {solver.instance.name}, p = {solver.p}, alpha = {solver.alpha} ..."
        )

        row = [name, solver.instance.index, solver.p, solver.alpha]

        gfs = GraspFinalSolver.from_solver(solver)
        write_solver_pickle(gfs, FINAL_PATH)
        afvs_record = gfs._grasp_final(iters, beta, time)

        users_stats = gfs.get_users_per_center_stats()

        row.extend(afvs_record)
        row.append(gfs.solution.time)
        row.append(gfs.solution.last_improvement)
        row.extend(users_stats.to_tuple())

        datalist.append(row)

    headers = [
        "instance",
        "i",
        "p",
        "alpha",
        "best_rgd",
        "best_afvs",
        "diff",
        "min_imp",
        "max_imp",
        "avg_imp",
        "time",
        "last_imp",
        "min_upc",
        "max_upc",
        "avg_upc",
    ]
    results = pd.DataFrame(datalist, columns=headers)

    filepath = os.path.join(FINAL_PATH, f"final_{name}.pkl")
    results.to_pickle(filepath)


def read_results(instance_name: str) -> pd.DataFrame:
    filepath = os.path.join(FINAL_PATH, f"final_{instance_name}.pkl")
    return pd.read_pickle(filepath)


def get_filenames() -> list[str]:
    """
    Searches the directory `FINAL_PATH` and returns a list of
    the filenames of the experiment results.
    """
    PREFIX = "final_"
    EXTENSION = ".pkl"

    filenames = [
        # remove prefix and extension from filename
        filename[len(PREFIX) :].split(".")[0]
        for filename in os.listdir(FINAL_PATH)
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
