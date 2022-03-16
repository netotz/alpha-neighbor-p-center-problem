from models.instance import Instance
from models.solver import Solver


instance = Instance.random(1000, 500)
solver = Solver(instance, 50, 3, True)
solver.plot(with_annotations=False, dpi=250)
solver.solution

solver.fast_swap()
solver.plot(with_annotations=False, dpi=250)

# solver.grasp(1, 0.4)
# args = dict(
#     is_first=True,
#     k=2
# )
# Solver.interchange(solver, **args)
