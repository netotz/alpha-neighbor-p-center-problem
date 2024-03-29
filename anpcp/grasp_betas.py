import math
import os

import numpy as np
import pandas as pd
import click

from utils import get_solvers
from models.solver import Solver


BETA_PATH = os.path.join("nb_results", "grasp", "betas")


@click.command()
@click.option(
    "-n", "--name", required=True, help="Instance name, without extension or index."
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
    default=[0.05, 0.1, 0.2],
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
    "--beta-space",
    type=float,
    default=0.2,
    show_default=True,
    help="""
    Spacing between values for beta. -1 will be added.
    
    e.g. -b 0.2 -> betas = [0, 0.2, 0.4, 0.6, 0.8, 1, -1]
    """,
)
@click.option(
    "-t",
    "--time",
    type=float,
    default=60 * 60 * 2,
    show_default=True,
    help="Time limit in seconds before stopping each GRASP (each beta). Use -1 for no limit.",
)
def __run(
    name: str,
    variations: int,
    p_percents: list[float],
    alpha_values: list[int],
    iters: int,
    beta_space: float,
    time: float,
):
    """
    Runs GRASP on all the configurations specified for an instance
    and creates a dataframe of the results intended to calibrate the beta parameter.
    """
    solvers = get_solvers(name, variations, p_percents, alpha_values)

    denominator = int(1 / beta_space)
    values = np.linspace(0, 1, denominator + 1)
    # prevent decimals like 0.60000000001
    betas = [round(b, 3) for b in values]
    betas.append(-1)

    print("Running...")
    results = calibrate(solvers, betas, iters, time)
    print("Finished.")

    filepath = os.path.join(BETA_PATH, f"betas_{name}_t{time}.pkl")
    results.to_pickle(filepath)


def calibrate(solvers: list[Solver], betas: list[float], iters: int, time_limit: float):
    datalist = []
    for solver in solvers:
        row = [solver.instance.index, solver.p, solver.alpha]

        best_of = math.inf
        obj_funcs = []
        # total time taken by each solution
        times = []
        # iterations where last improvement occurred
        improvements = []
        # run grasp for each beta
        for beta in betas:
            solver.grasp(iters, beta, time_limit)
            times.append(solver.solution.time)
            improvements.append(solver.solution.last_improvement)

            obj_func = solver.solution.obj_func
            obj_funcs.append(obj_func)

            best_of = min(best_of, obj_func)

        row.extend(obj_funcs)
        # calculate relative increase of each OF with respect to the best one
        row.extend([100 * (of - best_of) / best_of for of in obj_funcs])
        row.extend(times)
        row.extend(improvements)

        datalist.append(row)

    headers = "i p alpha".split()
    headers.extend([str(b) for b in betas] * 4)

    return pd.DataFrame(datalist, columns=headers)


def read_results(instance_name: str):
    filepath = os.path.join(BETA_PATH, f"betas_{instance_name}.pkl")
    return pd.read_pickle(filepath)


if __name__ == "__main__":
    __run()
