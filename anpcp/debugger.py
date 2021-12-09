from models import Solver, Instance


instance = Instance.random(100)
solver = Solver(instance, 10, 2)
solver.grasp(1, 0.4)
# args = dict(
#     is_first=True,
#     k=2
# )
# Solver.interchange(solver, **args)
