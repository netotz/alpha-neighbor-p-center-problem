import os

import pandas as pd

from models.instance import Instance
from models.solver import generate_solvers
from utils import compare_betas


def get_solvers(n: int, m: int, amount: int):
    datapath = os.path.abspath("..\\data")
    instances = [
        Instance.read_json(os.path.join(datapath, f"anpcp_{n}_{m}_{i}.json"))
        for i in range(amount)
    ]
    return generate_solvers(instances, (0.1, 0.25, 0.5), (2, 3))


def read_results():
    filepath = ".\\nb_results\\grasp\\betas.pkl"
    return pd.read_pickle(filepath)


def __run():
    solvers50 = get_solvers(50, 50, 5)
    solvers100 = get_solvers(100, 100, 5)
    solvers500 = get_solvers(500, 500, 5)
    solvers = solvers50 + solvers100 + solvers500

    # beta = -1 means that beta is selected at random in each iteration
    BETAS = (0, 0.25, 0.5, 0.75, 1, -1)

    results = compare_betas(solvers, BETAS)

    filepath = ".\\nb_results\\grasp\\betas.pkl"
    results.to_pickle(filepath)


if __name__ == "__main__":
    print("Running...")
    __run()
    print("Finished.")
