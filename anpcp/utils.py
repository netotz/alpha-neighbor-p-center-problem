from collections import defaultdict
from copy import deepcopy
import timeit
from typing import Any, Dict, Iterable, Mapping, Callable, Optional, Set

from models.solver import Solver

import pandas as pd


def compare_local_search(
    solvers: Iterable[Solver], is_first_improvement: bool, from_random: bool
) -> pd.DataFrame:
    """
    Runs and measures both local search algorithms on `solvers`.
    If `from_random`, the initial solution for the local search will be random,
    otherwise, the initial solution will be greedily constructed (beta = 0).
    """
    datalist = list()

    for solver in solvers:
        if from_random:
            initial = solver.randomize_solution()
        else:
            initial = solver.construct()

        initial = deepcopy(solver.solution)
        solver.history.append(initial)

        start = timeit.default_timer()
        solver.interchange(is_first_improvement)
        solver.solution.time = timeit.default_timer() - start
        ni = deepcopy(solver.solution)

        solver.solution = deepcopy(initial)

        start = timeit.default_timer()
        solver.fast_vertex_substitution(is_first_improvement)
        solver.solution.time = timeit.default_timer() - start
        fvs = deepcopy(solver.solution)

        initial_of = initial.get_obj_func()
        ni_of = ni.get_obj_func()
        fvs_of = fvs.get_obj_func()

        datalist.append(
            (
                solver.instance.n,
                solver.instance.m,
                solver.p,
                solver.alpha,
                initial_of,
                ni_of,
                ni.time,
                100 * abs(ni_of - initial_of) / initial_of,
                fvs_of,
                fvs.time,
                100 * abs(fvs_of - initial_of) / initial_of,
            )
        )

    # dataframe = pd.DataFrame.from_dict(datadict)
    dataframe = pd.DataFrame(
        datalist,
        columns="n,m,p,alpha,OF,OF,time,improvement,OF,time,improvement".split(","),
    )
    dataframe = pd.concat(
        {
            "instance": dataframe.iloc[:, range(4)],
            "RGD": dataframe.iloc[:, 4],
            "NI": dataframe.iloc[:, range(5, 8)],
            "FVS": dataframe.iloc[:, range(8, 11)],
        },
        axis=1,
    )

    return dataframe


def format_latex_table(dataframe: pd.DataFrame, path: str) -> None:
    def format_time(time: float) -> str:
        return f"{time:.3f}"

    def format_improvement(improvement: float) -> str:
        return f"{improvement:.1f}%"

    formatters = {
        ("NI", "time"): format_time,
        ("NI", "improvement"): format_improvement,
        ("FVS", "time"): format_time,
        ("FVS", "improvement"): format_improvement,
    }

    dataframe.to_latex(path, formatters=formatters)


def get_stats_df(
    solvers: Iterable[Solver],
    constructive: Optional[Callable[..., Set[int]]],
    local_search: Callable[..., Set[int]],
    args: Mapping[str, Any],
) -> pd.DataFrame:
    """
    TODO: Refactor to include Solution class.

    Formats the statistics of each solver as a DataFrame.

    Both `constructive` and `local_search` need to be a method of `Solver` class,
    e.g. `constructive=Solver.pdp_based`.

    `args` is a dictionary of custom arguments for local search methods.
    """
    data = list()
    for solver in solvers:
        start = timeit.default_timer()
        if constructive:
            constructive(solver)
            constructive_name = constructive.__name__
        else:
            solver.set_random_solution()
            constructive_time = 0
            constructive_name = "random"
        constructive_time = timeit.default_timer() - start
        constructive_of = solver.objective_function

        start = timeit.default_timer()
        if local_search:
            local_search(solver, **args)
            local_search_time = timeit.default_timer() - start

            strategy = "first" if args["is_first"] else "best"
            local_search_name = f"{local_search.__name__}_{strategy}_{args['k']}"

        data.append(
            (
                solver.instance.m,
                solver.p,
                solver.alpha,
                constructive_name,
                constructive_of,
                constructive_time,
                local_search_name,
                solver.objective_function,
                local_search_time,
            )
        )

    common_cols = ("heuristic", "OF", "seconds")
    df = pd.DataFrame(data, columns=("n", "p", "alpha", *common_cols * 2))

    params = df.loc[:, ("n", "p", "alpha")]
    # create column multiindex
    params = pd.concat({"instance": params}, axis=1)

    stats = (
        # create column multiindexes
        pd.concat(
            {
                "constructive": df.iloc[:, [3, 4, 5]],
                "local search": df.iloc[:, [6, 7, 8]],
            },
            axis=1,
        ).join(params)
        # reorder multiindexes and columns
        .loc[
            :,
            (
                ("instance", "constructive", "local search"),
                ("n", "p", "alpha", *common_cols),
            ),
        ]
    )

    stats["improvement", "absolute"] = (
        stats["constructive", "OF"] - stats["local search", "OF"]
    )
    stats["improvement", "relative %"] = (
        stats["improvement", "absolute"] / stats["constructive", "OF"]
    ) * 100

    return stats


def add_improvement_stats(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Adds how many improvements were made and the average of results.

    `dataframe` needs to be the return value of `get_stats_df`,
    but filtered by instance paramaters.
    """
    stats = dataframe.copy()
    improved = [
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        stats[stats["improvement", "absolute"] > 0].count()[0],
        "",
        "",
        "",
    ]
    average = [
        stats[top, sub].mean()
        if sub in {"OF", "seconds", "absolute", "relative %"}
        else ""
        for top, sub in stats.columns
    ]

    stats.loc["number improved"] = improved
    stats.loc["average"] = average

    return stats


def filter_dataframe(dataframe: pd.DataFrame) -> Dict[int, Any]:
    return {
        n: {
            p: {
                alpha: add_improvement_stats(
                    dataframe[
                        (dataframe["instance", "n"] == n)
                        & (dataframe["instance", "p"] == p)
                        & (dataframe["instance", "alpha"] == alpha)
                    ]
                )
                for alpha in dataframe["instance", "alpha"].unique()
            }
            for p in dataframe["instance", "p"].unique()
        }
        for n in dataframe["instance", "n"].unique()
    }
