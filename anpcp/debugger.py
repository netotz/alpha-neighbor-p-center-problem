import os

from models.instance import Instance
from models.solver import Solver

names = [
    "pr1002_668_334_4.anpcp.tsp",  # 0
    "rl1323_882_441_0.anpcp.tsp",
    "rat783_522_261_0.anpcp.tsp",  # 2
    "anpcp_882_441_0.json",
]
filepath = os.path.abspath(f"..\\data\\{names[3]}")
instance = (
    Instance.read_tsp(filepath)
    if filepath.endswith(".tsp")
    else Instance.read_json(filepath)
)

solver = Solver(instance, 20, 3, False)

# solver.grasp_iters_detailed(10, -1)
# solver.grasp(50)
