# %%
import os

# from grasp_pr import ExperimentalSolver, LocalSearchAlgorithm
from models.instance_same_set import InstanceSameSet
from models.solver_same_set import SolverSameSet
from models.instance import Instance
from models.solver import Solver
from models.solution_set import SolutionSet
from models.plotter import plot_solver

from utils import generate_solvers

# instance = Instance.random(100, 100, seed=20230918)
# solver = Solver(instance, 10, 2, True)

# r = solver.solution
# g = solver.grasp(100, 25, pool_limit=solver.p)
# pr = solver.path_relink(
#     SolutionSet.from_solution(r),
#     SolutionSet.from_solution(g),
# )

# _ = 1

# %%

DATA_PATH = os.path.join(
    "C:\\Users\\netoo\\local-personal\\repos\\alpha-neighbor-p-center-problem", "data"
)

names = [
    "pr1002_668_334_4.anpcp.tsp",  # 0
    "rl1323_882_441_0.anpcp.tsp",
    "rat783_522_261_0.anpcp.tsp",  # 2
    "anpcp_882_441_0.json",
    "dsj1000_750_250_0.anpcp.tsp",  # 4
    "nrw1379_920_459_0.anpcp.tsp",
    "ch150_100_50_0.anpcp.tsp",  # 6
    "rd400_267_133_0.anpcp.tsp",
    "vm1748_1166_582_0.anpcp.tsp",  # 8
    "rl1889_1260_629_0.anpcp.tsp",
    "att48_32_16_0.anpcp.tsp",  # 10
    "pr439_293_146_0.anpcp.tsp",
    "rat575_384_191_0.anpcp.tsp",  # 12
    "att48_24_24_0.anpcp.tsp",
]
filepath = os.path.join(DATA_PATH, names[13])
instance = Instance.read(filepath)

# %%
solver = Solver(instance, 5, 2, seed=20240131)

solver.grasp(100, 10, 1800, False)

# prs = ExperimentalSolver.from_solver(solver)
# prs.pr_algorithm = LocalSearchAlgorithm.AFVS
# prs.grasp(100, 25, 1800, 20)

# # %%
# instance = Instance.random(10, 10, seed=20230620)
# solver = Solver(instance, 5, 2, True)

# # %%

# # solver.grasp(50, -1)
# # solver.construct()
# # solver.fast_vertex_substitution(True)
# # solver.tabu_search(2, 35)
# # print(solver.solution)

# # %%

# names_same = [
#     "att48.tsp",  # 0
#     "ch150.tsp",
#     "pr439.tsp",  # 2
#     "rl1323.tsp",
# ]

# filepath = os.path.join(DATA_PATH, names_same[2])
# instance = InstanceSameSet.read(filepath)
# solver = SolverSameSet(instance, 40, 2)

# solver.construct()

# %%
