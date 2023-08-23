from dataclasses import dataclass
from functools import total_ordering
from .solution import Solution


@dataclass
@total_ordering
class SolutionSet:
    """
    Simpler version of `Solution` that only includes the set of open facilities S
    as `open_facilities` and the objective function value as `obj_func`.
    """

    obj_func: int | None = None
    open_facilities: set[int] | None = None

    @classmethod
    def from_solution(cls, solution: Solution) -> "SolutionSet":
        """
        Instantiates a `SolutionSet` from a `Solution` object.

        Time O(p) to copy the set of open facilities
        """
        return cls(solution.obj_func, solution.open_facilities.copy())

    def __eq__(self, __other: "SolutionSet") -> bool:
        return self.obj_func == __other.obj_func

    def __lt__(self, __other: "SolutionSet") -> bool:
        return self.obj_func < __other.obj_func

    def __le__(self, __other: "SolutionSet") -> bool:
        return self.obj_func <= __other.obj_func

    def __gt__(self, __other: "SolutionSet") -> bool:
        return self.obj_func > __other.obj_func

    def __ge__(self, __other: "SolutionSet") -> bool:
        return self.obj_func >= __other.obj_func

    def __ne__(self, __other: "SolutionSet") -> bool:
        return not self.__eq__(__other)
