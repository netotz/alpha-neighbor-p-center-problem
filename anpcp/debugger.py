from models import Solver, Instance

instance = Instance.random(10, 5)
solver = Solver(instance, 3, 2)
solver.grasp(1, 0.4)
# args = dict(
#     is_first=True,
#     k=2
# )
# Solver.interchange(solver, **args)
