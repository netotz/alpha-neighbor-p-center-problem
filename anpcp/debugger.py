import os
from models.instance import Instance
from models.solver import Solver

filepath = os.path.abspath("..\\data\\pr1002_668_334_0.anpcp.tsp")
instance = Instance.read_tsp(filepath)

# instance = Instance.random(100, 100)
solver = Solver(instance, 44, 3, True)

solver.grasp(50)
