import os

import pandas as pd
import click

from models.solver import Solver
from models.instance import Instance


def read_results(instance_name: str):
    filepath = f".\\nb_results\\grasp\\iters_{instance_name}.pkl"
    return pd.read_pickle(filepath)


@click.command()
@click.option("-n", "--name", required=True, help="instance name, without extension")
@click.option("-p", "--p", type=int, required=True, help="p")
@click.option("-a", "--alpha", type=int, required=True, help="alpha")
@click.option(
    "-i", "--iters", default=5000, show_default=True, help="maximum iterations"
)
@click.option("-b", "--beta", default=-1.0, show_default=True, help="beta for RCL")
def __run(name: str, p: int, alpha: int, iters: int = 5000, beta: float = -1):
    """
    CLI to run iterations experiment on `name` instance.
    """
    datapath = os.path.abspath("..\\data")
    extension = ".json" if name.startswith("anpcp_") else ".anpcp.tsp"
    filepath = os.path.join(datapath, f"{name}{extension}")

    instance = Instance.read_json(filepath)
    solver = Solver(instance, p, alpha)

    print("Running...")
    results = solver.grasp_iters_detailed(iters, beta)
    print("Finished.")

    filename = f"iters_{name}_p{p}_a{alpha}.pkl"
    filepath = f".\\nb_results\\grasp\\{filename}"
    results.to_pickle(filepath)


if __name__ == "__main__":
    __run()
