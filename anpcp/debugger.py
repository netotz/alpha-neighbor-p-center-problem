import os
from models.instance import Instance
from models.solver import Solver

filepath = os.path.abspath("..\\data\\ch150_100_50_0.anpcp.tsp")
instance = Instance.read_tsp(filepath)

instance = Instance.random(100, 100)
solver = Solver(instance, 10, 2, True)

solver.grasp(50)
