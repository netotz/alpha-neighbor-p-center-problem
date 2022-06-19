import os

import pandas as pd

from models.instance import Instance
from models.solver import Solver
from utils import run_grasp


def get_solvers(names, amount: int):
    datapath = os.path.abspath("..\\data")

    instances = [
        Instance.read_tsp(os.path.join(datapath, f"{name}_{i}.anpcp.tsp"))
        for name in names
        for i in range(amount)
    ]

    return [
        Solver(instance, p, alpha)
        for instance in instances
        for p in range(10, 101, 10)
        if p < instance.m
        for alpha in (2, 3)
    ]


def read_results():
    filepath = ".\\nb_results\\grasp\\final.pkl"
    return pd.read_pickle(filepath)


def __run():
    names = [
        "att48_32_16",
        "eil101_68_33",
        "ch150_100_50",
        "pr439_293_146",
        "rat575_384_191",
        "rat783_522_261",
        "pr1002_668_334",
        "rl1323_882_441",
    ]
    solvers = get_solvers(names, 5)

    results = run_grasp(solvers)

    filepath = ".\\nb_results\\grasp\\final.pkl"
    results.to_pickle(filepath)


if __name__ == "__main__":
    print("Running...")
    __run()
    print("Finished.")
