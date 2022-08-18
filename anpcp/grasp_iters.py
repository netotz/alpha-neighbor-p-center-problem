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

    if name.startswith("anpcp_"):
        extension = ".json"
        reader = Instance.read_json
    else:
        extension = ".anpcp.tsp"
        reader = Instance.read_tsp

    filepath = os.path.join(datapath, f"{name}{extension}")

    # TODO: move reader selection into Instance class
    instance = reader(filepath)
    solver = Solver(instance, p, alpha)

    print("Running...")
    results = solver.grasp_iters_detailed(iters, beta)
    print("Finished.")

    filename = f"iters_{name}_p{p}_a{alpha}.pkl"
    filepath = os.path.join("nb_results", "grasp", filename)
    results.to_pickle(filepath)


if __name__ == "__main__":
    __run()
