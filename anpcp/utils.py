from copy import deepcopy
import timeit
from typing import (
    Any,
    Dict,
    Iterable,
    Mapping,
    Callable,
    Optional,
    Set,
    Tuple,
)

from models.solution import Solution
from models.solver import Solver

import pandas as pd


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

    initial_of = initial_solution.get_obj_func()
    ni_of = ni.get_obj_func()
    fvs_of = fvs.get_obj_func()

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


def compare_betas(solvers: Iterable[Solver], betas: Iterable[float]):
    """
    Compares the results of running GRASP with different values for beta (RGD).
    The resulting dataframe is not grouped.
    """
    datalist = list()

    MAX_ITERS = 100

    for solver in solvers:
        for beta in betas:
            solver.grasp(MAX_ITERS, beta)
            obj_func = solver.solution.get_obj_func()

            datalist.append(
                (
                    solver.instance.tsp_name,
                    solver.instance.n,
                    solver.instance.m,
                    solver.p,
                    solver.alpha,
                    beta,
                    obj_func,
                    solver.solution.time,
                    solver.solution.moves,
                )
            )

    dataframe = pd.DataFrame(
        datalist, columns="tsp n m p alpha beta OF time improvs".split()
    )
    return dataframe


def run_grasp(solvers: Iterable[Solver]):
    datalist = list()

    MAX_ITERS = 50

    for solver in solvers:
        solver.grasp(MAX_ITERS, 0)
        obj_func = solver.solution.get_obj_func()

        datalist.append(
            (
                solver.instance.tsp_name,
                solver.instance.n,
                solver.instance.m,
                solver.p,
                solver.alpha,
                obj_func,
                solver.solution.time,
                solver.solution.moves,
            )
        )

    dataframe = pd.DataFrame(
        datalist, columns="tsp n m p alpha OF time improvs".split()
    )
    return dataframe.groupby("tsp n m p alpha ".split()).mean()
