import timeit
from typing import Any, Iterable, Mapping, Callable, Set

from models.solver import Solver

import pandas as pd


def get_stats_df(
            solvers: Iterable[Solver],
            constructive: Callable[..., Set[int]],
            local_search: Callable[..., Set[int]],
            args: Mapping[str, Any]
        ) -> pd.DataFrame:
    data = list()
    for solver in solvers:
        start = timeit.default_timer()
        if constructive:
            constructive(solver)
            constructive_time = timeit.default_timer() - start
            constructive_of = solver.objective_function
            constructive_name = constructive.__name__
        else:
            solver.set_random_solution()
            constructive_time = -1
            constructive_name = "random"

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

    df = pd.DataFrame(
        data,
        columns=(
            'n', 'p', 'alpha',
            'heuristic',
            'OF', 'seconds',
            'heuristic',
            'OF', 'seconds'
        )
    )

    params = df.loc[:, ('n', 'p', 'alpha')]
    params = pd.concat({'instance': params}, axis=1)

    stats = (
        pd.concat(
            {
                'constructive': df.iloc[:, [3, 4, 5]],
                'local search': df.iloc[:, [6, 7, 8]]
            },
            axis=1
        )
        .join(params)
        .loc[:, (
            ('instance', 'constructive', 'local search'),
            ('n', 'p', 'alpha', 'heuristic', 'OF', 'seconds')
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

    stats.loc['improved'] = improved
    stats.loc['average'] = average

    return stats
