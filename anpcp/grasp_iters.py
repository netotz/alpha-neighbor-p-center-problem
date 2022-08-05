import os

import pandas as pd

from models.solver import Solver
from models.instance import Instance


def read_results():
    filepath = ".\\nb_results\\grasp\\iters.pkl"
    return pd.read_pickle(filepath)


def __run():
    datapath = os.path.abspath("..\\data")

    name = "rl1323_882_441"
    filepath = os.path.join(datapath, f"{name}_0.anpcp.tsp")
    instance = Instance.read_tsp(filepath)
    solver = Solver(instance, 44, 3)

    MAX_ITERS = 5000
    RAND_BETA = -1
    results = solver.grasp_iters_detailed(MAX_ITERS, RAND_BETA)

    filepath = ".\\nb_results\\grasp\\iters.pkl"
    results.to_pickle(filepath)


if __name__ == "__main__":
    print("Running...")
    __run()
    print("Finished.")
