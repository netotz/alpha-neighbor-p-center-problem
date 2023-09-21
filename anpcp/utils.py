from copy import deepcopy
import os
import timeit
from typing import Iterable, Tuple, Sequence

import pandas as pd

from models.instance import Instance
from models.solution import Solution
from models.solver import Solver


DATA_PATH = os.path.join("..", "data")


def compare_local_search(solvers: Iterable[Solver], from_random: bool):
    """
    Runs and measures the NI and A-FVS local search algorithms on `solvers`,
    with 2 strategies IF and IB.

    If `from_random`, the initial solution will be random,
    otherwise, the initial solution will be greedily constructed (beta = 0).
    """
    datalist_if = list()
    datalist_ib = list()

    for solver in solvers:
        initial = deepcopy(
            solver.randomize_solution() if from_random else solver.construct()
        )

        datalist_if.append(run_local_search(solver, True, initial))
        solver.solution = deepcopy(initial)
        datalist_ib.append(run_local_search(solver, False, initial))

    initial_header = "rand" if from_random else "RGD"
    dataframe_if = create_dataframe_local_search(datalist_if, initial_header)
    dataframe_ib = create_dataframe_local_search(datalist_ib, initial_header)

    return dataframe_if, dataframe_ib


def run_local_search(
    solver: Solver, is_first_improvement: bool, initial_solution: Solution
):
    start = timeit.default_timer()
    solver.interchange(is_first_improvement)
    solver.solution.time = timeit.default_timer() - start
    ni = deepcopy(solver.solution)

    solver.solution = deepcopy(initial_solution)

    start = timeit.default_timer()
    solver.fast_vertex_substitution(is_first_improvement)
    solver.solution.time = timeit.default_timer() - start
    fvs = deepcopy(solver.solution)

    initial_of = initial_solution.obj_func
    ni_of = ni.obj_func
    fvs_of = fvs.obj_func

    return (
        solver.instance.n,
        solver.instance.m,
        solver.p,
        solver.alpha,
        initial_of,
        ni_of,
        100 * abs(ni_of - initial_of) / initial_of,
        ni.time,
        ni.moves,
        fvs_of,
        100 * abs(fvs_of - initial_of) / initial_of,
        fvs.time,
        fvs.moves,
    )


def create_dataframe_local_search(data: Iterable[Tuple], initial_header: str):
    dataframe = pd.DataFrame(
        data,
        columns="n m p alpha OF OF improvement time moves OF improvement time moves".split(),
    )

    mean_dataframe = dataframe.groupby("n m p alpha".split()).mean()
    # create multiindex
    mean_dataframe = pd.concat(
        {
            initial_header: mean_dataframe.iloc[:, 0],
            "NI": mean_dataframe.iloc[:, range(1, 5)],
            "A-FVS": mean_dataframe.iloc[:, range(5, 9)],
        },
        axis=1,
    )

    return mean_dataframe


def format_latex_table(dataframe: pd.DataFrame, path: str):
    dataframe.to_latex(path, float_format="%.2f", multirow=True)


def generate_solvers(
    instances: Sequence[Instance],
    p_percentages: Sequence[float],
    alpha_values: Sequence[int],
) -> list[Solver]:
    return [
        Solver(instance, int(instance.m * p), alpha)
        for instance in instances
        for p in p_percentages
        for alpha in alpha_values
    ]


def get_solvers(
    name: str, amount: int, p_percents: list[float], alpha_values: list[int]
) -> list[Solver]:
    if name.startswith("anpcp_"):
        extension = ".json"
    else:
        extension = ".anpcp.tsp"

    instances = []
    for i in range(amount):
        filepath = os.path.join(DATA_PATH, f"{name}_{i}{extension}")
        # if variant i doesn't exist
        if not os.path.exists(filepath):
            continue

        instances.append(Instance.read(filepath))

    return generate_solvers(instances, p_percents, alpha_values)
