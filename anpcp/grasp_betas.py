import os

import pandas as pd

from models.instance import Instance
from models.solver import generate_solvers
from utils import compare_betas


def get_solvers(names, amount: int):
    datapath = os.path.abspath("..\\data")

    instances = [
        Instance.read_tsp(os.path.join(datapath, f"{name}_{i}.anpcp.tsp"))
        for name in names
        for i in range(amount)
    ]
    return generate_solvers(instances, (0.1, 0.25, 0.5), (2, 3))


def read_results():
    filepath = ".\\nb_results\\grasp\\betas.pkl"
    return pd.read_pickle(filepath)


def __run():
    names = ["ch150_100_50", "rat575_384_191", "pr1002_668_334"]
    solvers = get_solvers(names, 3)

    # beta = -1 means that beta is selected at random in each iteration
    BETAS = (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, -1)

    results = compare_betas(solvers, BETAS)

    filepath = ".\\nb_results\\grasp\\betas.pkl"
    results.to_pickle(filepath)


if __name__ == "__main__":
    print("Running...")
    __run()
    print("Finished.")
