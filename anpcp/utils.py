import timeit
from typing import Any, Iterable, Mapping, Callable, Optional, Set

from models.solver import Solver

import pandas as pd


def get_stats_df(
            solvers: Iterable[Solver],
            constructive: Optional[Callable[..., Set[int]]],
            local_search: Callable[..., Set[int]],
            args: Mapping[str, Any]
        ) -> pd.DataFrame:
    '''
    Formats the statistics of each solver as a DataFrame.

    Both `constructive` and `local_search` need to be a method of `Solver` class,
    e.g. `constructive=Solver.pdp_based`.

    `args` is a dictionary of custom arguments for local search methods.
    '''
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
            
            strategy = 'first' if args['is_first'] else 'best'
            local_search_name = f"{local_search.__name__}_{strategy}_{args['k']}"

        data.append((
            solver.instance.n,
            solver.instance.p,
            solver.instance.alpha,
            constructive_name,
            constructive_of,
            constructive_time,
            local_search_name,
            solver.objective_function,
            local_search_time
        ))

    common_cols = ('heuristic', 'OF', 'seconds')
    df = pd.DataFrame(
        data,
        columns=(
            'n', 'p', 'alpha',
            *common_cols * 2
        )
    )

    params = df.loc[:, ('n', 'p', 'alpha')]
    # create multiindex
    params = pd.concat({'instance': params}, axis=1)

    stats = (
        # create multiindexes
        pd.concat(
            {
                'constructive': df.iloc[:, [3, 4, 5]],
                'local search': df.iloc[:, [6, 7, 8]]
            },
            axis=1
        )
        .join(params)
        # reorder multiindexes and columns
        .loc[:, (
            ('instance', 'constructive', 'local search'),
            ('n', 'p', 'alpha', *common_cols)
        )]
    )

    stats['improvement', 'absolute'] = stats['constructive', 'OF'] - stats['local search', 'OF']
    stats['improvement', 'relative %'] = (stats['improvement', 'absolute'] / stats['constructive', 'OF']) * 100
    improved = [
        '', '', '', '', '', '', '',
        int((stats['improvement', 'absolute'] > 0).count()),
        '', '', ''
    ]
    average = [
        stats[top, sub].mean()
        if sub in {'OF', 'seconds', 'absolute', 'relative %'}
        else ''
        for top, sub in stats.columns
    ]

    stats.loc['number improved'] = improved
    stats.loc['average'] = average

    return stats
