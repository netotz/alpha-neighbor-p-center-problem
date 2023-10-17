from typing import Iterator

from .solution_set import SolutionSet
from .elite_differences_heap import EliteDifferencesHeap

ObjFuncIndexTuple = tuple[int, int]


class ElitePool:
    def __init__(self, limit: int, min_symmetric_difference: int = 4) -> None:
        """
        `limit`: Max amount of solutions in pool. Must be positive, else raises a `ValueError`.

        `min_symmetric_difference`: Minimum symmetric difference between a candidate solution
        and the current pool.
        """

        self.__solutions: list[SolutionSet] = []
        """
        List of solutions in pool, used to access by indexes from `__maxheap`.
        """

        self.__last_i = 0
        """
        Index in `__solutions` of last inserted or updated solution.
        """

        self.__best_i: int | None = None
        """
        Index in `__solutions` of best solution.
        """

        self.__worst_i: int | None = None
        """
        Index in `__solutions` of worst solution.
        """

        if limit <= 0:
            raise ValueError("Limit must be positive.")
        else:
            self.limit = limit

        if min_symmetric_difference < 0:
            raise ValueError("Minimum symmetric difference must be zero or greater.")
        else:
            self.min_symmetric_difference = min_symmetric_difference

    def try_add(self, candidate: SolutionSet) -> bool:
        """
        Tries to add `solution` to the current pool.

        Time O(pl)
        """
        # O(pl)
        diffs_heap = EliteDifferencesHeap(
            candidate,
            self.__solutions,
            self.min_symmetric_difference,
        )

        if not diffs_heap.is_symmetrically_different:
            return False

        is_added = False

        if not self.is_full():
            self.__append_solution(candidate)

            is_added = True
        elif candidate < self.get_worst():
            index = diffs_heap.get_index_to_replace()
            self.__replace_solution(candidate, index)

            is_added = True

        if is_added:
            self.__try_update_best_i(candidate)
            self.__try_update_worst_i(candidate)

        return is_added

    def get_best(self) -> SolutionSet | None:
        return None if self.__best_i is None else self.__solutions[self.__best_i]

    def get_worst(self) -> SolutionSet | None:
        return None if self.__worst_i is None else self.__solutions[self.__worst_i]

    def iter_solutions(self) -> Iterator[SolutionSet]:
        for solution in self.__solutions:
            yield solution

    def __append_solution(self, new: SolutionSet) -> None:
        """
        Adds `solution` to inner list and updates `self.__last_i`.

        Time O(1)
        """
        self.__solutions.append(new)
        self.__last_i = len(self.__solutions) - 1

    def __replace_solution(self, new: SolutionSet, index: int) -> None:
        """
        Replaces the solution at `index` with `new`
        and updates `self.__last_i`.

        Time O(1)
        """
        self.__solutions[index] = new
        self.__last_i = index

    def __try_update_best_i(self, candidate: SolutionSet) -> bool:
        if self.__best_i is not None and candidate >= self.get_best():
            return False

        self.__best_i = self.__last_i

        return True

    def __try_update_worst_i(self, candidate: SolutionSet) -> bool:
        if self.__worst_i is not None and candidate <= self.get_worst():
            return False

        self.__worst_i = self.__last_i

        return True

    def is_full(self) -> bool:
        return len(self) == self.limit

    def __len__(self) -> int:
        return len(self.__solutions)
