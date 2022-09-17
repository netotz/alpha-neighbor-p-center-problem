from copy import deepcopy
from dataclasses import dataclass
from itertools import chain
import math
import os
import random
import timeit

import pandas as pd

from models.solver import Solver
from models.min_max_avg import MinMaxAvg
from utils import get_solvers


@dataclass
class GraspAfvsRecord:
    best_rgd_of: int
    best_afvs_of: int
    best_rgd_diff: float
    afvs_improvement_stats: MinMaxAvg


class GraspFinalSolver(Solver):
    def _grasp_final(self, iters: int, beta: float, time_limit: float = -1):
        """
        Modified method for final experiments of GRASP.
        """
        if time_limit == -1:
            time_limit = math.inf

        best_solution = None
        best_rgd_of = best_afvs_of = math.inf

        # relative improvements by local search AFVS
        min_afvs_improvement = math.inf
        max_afvs_improvement = -math.inf
        afvs_improvements_sum = 0

        total_time = moves = 0

        last_imp = i = iwi = 0
        while iwi < iters and total_time < time_limit:
            self.init_solution()

            beta_used = random.random() if beta == -1 else beta

            start = timeit.default_timer()
            self.construct(beta_used)
            total_time += timeit.default_timer() - start

            rgd_of = self.solution.get_obj_func()
            best_rgd_of = min(best_rgd_of, rgd_of)

            start = timeit.default_timer()
            self.fast_vertex_substitution(True)
            total_time += timeit.default_timer() - start

            afvs_of = self.solution.get_obj_func()
            afvs_improvement = 100 * abs(afvs_of - rgd_of) / rgd_of
            min_afvs_improvement = min(min_afvs_improvement, afvs_improvement)
            max_afvs_improvement = max(max_afvs_improvement, afvs_improvement)
            afvs_improvements_sum += afvs_improvement

            if best_solution is None or afvs_of < best_afvs_of:
                best_solution = deepcopy(self.solution)
                best_afvs_of = afvs_of
                moves += 1

                iwi = 0
                last_imp = i
            else:
                iwi += 1
            i += 1

        self.solution = deepcopy(best_solution)
        self.solution.time = total_time
        self.solution.moves = moves
        self.solution.last_improvement = last_imp

        avg_afvs_improvement = afvs_improvements_sum / i
        best_rgd_diff = 100 * abs(best_afvs_of - best_rgd_of) / best_rgd_of

        afvs_improvement_stats = MinMaxAvg(
            min_afvs_improvement, max_afvs_improvement, avg_afvs_improvement
        )

        return GraspAfvsRecord(
            best_rgd_of,
            best_afvs_of,
            best_rgd_diff,
            afvs_improvement_stats,
        )


FINAL_PATH = os.path.join("nb_results", "grasp", "final")

# calibrated parameters
BETA = 0.2
ITERATIONS = 100

# arbitrary limit, 30 minutes
TIME_LIMIT = 1800


def read_results(instance_name: str) -> pd.DataFrame:
    filepath = os.path.join(FINAL_PATH, f"final_{instance_name}.pkl")
    return pd.read_pickle(filepath)


def __run():
    names = [
        "pr439_293_146",
        "rat575_384_191",
        "rat783_522_261",
        "dsj1000_667_333",
        "rl1323_882_441",
        "rl1889_1260_629",
    ]
    solvers: chain[Solver] = chain.from_iterable(
        get_solvers(name, 10) for name in names
    )

    for solver in solvers:
        gfs = GraspFinalSolver.from_solver(solver)
        afvs_record = gfs._grasp_final(ITERATIONS, BETA, TIME_LIMIT)

    # filepath = ".\\nb_results\\grasp\\final.pkl"
    # results.to_pickle(filepath)


if __name__ == "__main__":
    print("Running...")
    __run()
    print("Finished.")
