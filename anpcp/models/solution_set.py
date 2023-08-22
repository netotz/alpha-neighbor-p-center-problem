from dataclasses import dataclass

from .solution import Solution


@dataclass
class SolutionSet:
    """
    Simpler version of `Solution` that only includes the set of open facilities S
    as `open_facilities` and the objective function value as `obj_func`.
    """

    obj_func: int
    open_facilities: set[int]

    @classmethod
    def from_solution(cls, solution: Solution) -> "SolutionSet":
        """
        Instantiates a `SolutionSet` from a `Solution` object.

        Time O(p) to copy the set of open facilities
        """
        return cls(solution.get_obj_func(), solution.open_facilities.copy())
