from models.instance import Instance
from models.solver import Solver

instance = Instance.random(100, 50)
solver = Solver(instance, 5, 1, True)
solver.plot(with_annotations=False, dpi=250)
solver.fast_swap()
# solver.grasp(1, 0.4)
# args = dict(
#     is_first=True,
#     k=2
# )
# Solver.interchange(solver, **args)
