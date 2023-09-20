import itertools
import math
import timeit

import pandas as pd

from .elite_pool import ElitePool
from .instance import Instance
from .reactive_beta import ReactiveBeta
from .solution import Solution
from .solution_set import SolutionSet
from .solver import Solver


class ExperimentalSolver(Solver):
    """
    Extended version of `Solver` to run experiments only,
    it's not designed to be used for anything else.
    There's no guarantee that methods here will be maintained.
    """

    def __init__(
        self,
        instance: Instance,
        p: int,
        alpha: int,
        with_random_solution=False,
        is_first_improvement=True,
        seed: int | None = None,
    ):
        super().__init__(
            instance, p, alpha, with_random_solution, is_first_improvement, seed
        )

    def grasp_detailed_reactive(
        self,
        iters: int,
        beta_period: int = 1,
        time_limit: float = math.inf,
    ) -> pd.DataFrame:
        """
        Modified method of GRASP to experiment with reactive beta.
        This version doesn't run Path Relinking.
        """
        datalist = []

        # times of ReactiveBeta methods
        times: dict[str, float] = {
            "init": 0,
            "choose": 0,
            "increment": 0,
            "update": 0,
        }

        start = timeit.default_timer()

        start_temp = timeit.default_timer()
        reactive = ReactiveBeta(seed=self.seed)
        times["init"] = timeit.default_timer() - start_temp

        best_solution: SolutionSet | None = None

        total_time = moves = 0
        last_imp = i = iwi = 0

        while iwi < iters and total_time < time_limit:
            self.__init_solution()

            start_temp = timeit.default_timer()
            beta_used = reactive.choose()
            times["choose"] += timeit.default_timer() - start_temp

            # O(mp)
            self.construct(beta_used)
            # O(mpn)
            self.fast_vertex_substitution()

            start_temp = timeit.default_timer()
            reactive.increment(beta_used, self.solution.obj_func)
            times["increment"] += timeit.default_timer() - start_temp

            # O(p)
            current_solution = SolutionSet.from_solution(self.solution)

            if best_solution is None or current_solution < best_solution:
                best_solution = current_solution
                moves += 1

                iwi = 0
                last_imp = i
            else:
                iwi += 1

            # don't update reactive beta in first iteration
            if i > 0 and i % beta_period == 0:
                start_temp = timeit.default_timer()
                reactive.update(best_solution.obj_func)
                times["update"] += timeit.default_timer() - start_temp

            i += 1

        # O(mn)
        self.replace_solution(best_solution)

        total_time = timeit.default_timer() - start

        self.solution.time = total_time
        self.solution.moves = moves
        self.solution.last_improvement = last_imp

        # get time of each method and percentage of total_time
        # then flatten
        data = list(
            itertools.chain.from_iterable(
                (t, (100 * t) / total_time) for t in times.values()
            )
        )

        dataframe = pd.DataFrame(
            data,
            columns=" ".join(f"{k}_s {k}_%" for k in times.keys()).split(),
        )

        return dataframe
