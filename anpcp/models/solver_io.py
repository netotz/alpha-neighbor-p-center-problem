from dataclasses import dataclass
import os
import pickle

from .solution import Solution
from .solver import Solver
from .instance import Instance


@dataclass
class SolverDto:
    """
    Subset of `Solver` to save persistent data in pickle files.
    """

    instance_name: str
    p: int
    alpha: int
    solution: Solution


class SolverIO:
    """
    Handles the input and output of `Solver` class.
    """

    def __init__(self, solver: Solver):
        self.solver = solver
        self.dto = SolverDto(
            self.solver.instance.name,
            self.solver.p,
            self.solver.alpha,
            self.solver.solution,
        )

    def write_pickle(
        self,
        directory: str = os.path.curdir,
        extra_params: dict[str, str] | None = None,
    ) -> None:
        params_str = (
            ""
            if extra_params is None
            else "".join(f"_{k}{v}" for k, v in extra_params.items())
        )

        filename = f"solver_{self.solver.instance.name}_p{self.solver.p}_a{self.solver.alpha}{params_str}.pkl"
        filepath = os.path.join(directory, filename)

        # write binary
        with open(filepath, "wb") as file:
            pickle.dump(self.dto, file)


def write_solver_pickle(
    solver: Solver,
    directory: str = os.path.curdir,
    extra_params: dict[str, str] | None = None,
) -> None:
    """
    Writes `Solver` to a picke file (.pkl) inside "directory/".
    """
    SolverIO(solver).write_pickle(directory, extra_params)


def read_solver_pickle(instance: Instance, filepath: str) -> Solver:
    """
    Reads a `Solver` picke file (.pkl) and loads it with `instance`.
    """
    # read binary
    with open(filepath, "rb") as file:
        dto: SolverDto = pickle.load(file)

    solver = Solver(instance, dto.p, dto.alpha)
    solver.solution = dto.solution
    solver.update_obj_func()

    return solver
