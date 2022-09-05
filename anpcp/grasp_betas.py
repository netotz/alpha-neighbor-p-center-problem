import math
import os

import numpy as np
import pandas as pd
import click

from models.instance import Instance
from models.solver import Solver, generate_solvers


DATA_PATH = os.path.join("..", "data")
BETA_PATH = os.path.join("nb_results", "grasp", "betas")


def get_solvers(
    name: str, amount: int, p_percents: list[float], alpha_values: list[int]
):
    if name.startswith("anpcp_"):
        extension = ".json"
    else:
        extension = ".anpcp.tsp"

    instances = []
    for i in range(amount):
        filepath = os.path.join(DATA_PATH, f"{name}_{i}{extension}")
        # if variant i doesn't exist
        if not os.path.exists(filepath):
            break

        instances.append(Instance.read(filepath))

    return generate_solvers(instances, p_percents, alpha_values)


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
def __run(
    name: str,
    variations: int,
    p_percents: list[float],
    alpha_values: list[int],
    iters: int,
    beta_space: float,
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
    results = calibrate(solvers, betas, iters)
    print("Finished.")

    filepath = os.path.join(BETA_PATH, f"betas_{name}.pkl")
    results.to_pickle(filepath)


def calibrate(solvers: list[Solver], betas: list[float], iters: int):
    datalist = []
    for solver in solvers:
        row = [solver.instance.index, solver.p, solver.alpha]

        best_of = math.inf
        obj_funcs = []
        # run grasp for each beta
        for beta in betas:
            solver.grasp(iters, beta)

            obj_func = solver.solution.get_obj_func()
            obj_funcs.append(obj_func)

            best_of = min(best_of, obj_func)

        row.extend(obj_funcs)
        # calculate relative increase of each OF with respect to the best one
        row.extend([100 * (of - best_of) / best_of for of in obj_funcs])

        datalist.append(row)

    headers = "i p alpha".split()
    headers.extend(map(str, betas))
    headers.extend(f"d_{b}" for b in betas)

    return pd.DataFrame(datalist, columns=headers)


def read_results(instance_name: str):
    filepath = os.path.join(BETA_PATH, f"betas_{instance_name}.pkl")
    return pd.read_pickle(filepath)


if __name__ == "__main__":
    __run()
