import os

import pandas as pd

from models.solver import Solver
from models.instance import Instance


def read_results(instance_name: str):
    filepath = f".\\nb_results\\grasp\\iters_{instance_name}.pkl"
    return pd.read_pickle(filepath)


def __run():
    datapath = os.path.abspath("..\\data")

    # TSPLIB instances
    # name = "rl1323_882_441_0"
    # filepath = os.path.join(datapath, f"{name}.anpcp.tsp")
    # instance = Instance.read_tsp(filepath)

    # random generated instances
    name = "anpcp_882_441_0"
    filepath = os.path.join(datapath, f"{name}.json")
    instance = Instance.read_json(filepath)

    p = 20
    alpha = 3
    solver = Solver(instance, p, alpha)

    MAX_ITERS = 5000
    RAND_BETA = -1
    results = solver.grasp_iters_detailed(MAX_ITERS, RAND_BETA)

    filename = f"iters_{name}_p{p}_a{alpha}.pkl"
    filepath = f".\\nb_results\\grasp\\{filename}"
    results.to_pickle(filepath)


if __name__ == "__main__":
    print("Running...")
    __run()
    print("Finished.")
