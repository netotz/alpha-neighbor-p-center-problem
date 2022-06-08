import os
from utils import compare_local_search
from models.instance import Instance
from models.solver import Solver

# filepath = os.path.abspath("data\\anpcp_50_50_0.json")
# instance = Instance.read_json(filepath)

instance = Instance.random(100, 100)
solver = Solver(instance, 10, 2, True)

# solver.construct()
# solver.interchange(False)

solver.fast_vertex_substitution(True)
