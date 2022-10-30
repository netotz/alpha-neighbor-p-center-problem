import os

from models.instance import Instance
from models.solver import Solver
from models.plotter import plot_solver

#%%
DATA_PATH = os.path.join("..", "data")

#%%
names = [
    "pr1002_668_334_4.anpcp.tsp",  # 0
    "rl1323_882_441_0.anpcp.tsp",
    "rat783_522_261_0.anpcp.tsp",  # 2
    "anpcp_882_441_0.json",
    "dsj1000_750_250_0.anpcp.tsp",  # 4
    "nrw1379_920_459_0.anpcp.tsp",
    "ch150_100_50_0.anpcp.tsp",  # 6
    "rd400_267_133_0.anpcp.tsp",
    "vm1748_1166_582_0.anpcp.tsp",
    "rl1889_1260_629_0.anpcp.tsp",  # 6
    "att48_32_16_0.anpcp.tsp",
    "pr439_293_146_0.anpcp.tsp",  # 8
]
filepath = os.path.join(DATA_PATH, names[5])
instance = Instance.read(filepath)

solver = Solver(instance, 45, 2, False)

solver = Solver(instance, 20, 3, False)

# solver.grasp_iters_detailed(10, -1)
# solver.grasp(50)
