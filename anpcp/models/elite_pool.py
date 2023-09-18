import heapq
from typing import Iterator
from .solution_set import SolutionSet

ObjFuncIndexTuple = tuple[int, int]


class ElitePool:
    def __init__(self, limit: int) -> None:
        """
        `limit`: Max amount of solutions in pool. Must be positive, else raises a `ValueError`.
        """
        self.__maxheap: list[ObjFuncIndexTuple] = []
        """
        Max heap to track solutions by worse x(S), with tuples of type
        `[-obj_func, index in __solutions]`.
        """
        self.__solutions: list[SolutionSet] = []
        """
        List of solutions in pool, used to access by indexes from `__maxheap`.
        """

        self.__last_i = 0
        """
        Index in `__solutions` of last inserted solution.
        """
        self.__best_i: int | None = None
        """
        Index in `__solutions` of best solution.
        """

        if limit <= 0:
            raise ValueError("Limit must be positive.")
        else:
            self.limit = limit

    def try_add(self, solution: SolutionSet) -> bool:
        """
        Tries to add `solution` to the current pool.

        Time O(log l)
        """
        is_added = False

        if len(self) < self.limit:
            # O(log l)
            self.__add_max(solution)
            is_added = True
        elif solution <= self.get_worst():
            # O(log l)
            self.__update_worst(solution)
            is_added = True

        if is_added:
            self.__try_update_best(solution)

        return is_added

    def get_best(self) -> SolutionSet:
        return None if self.__best_i is None else self.__solutions[self.__best_i]

    def get_worst(self) -> SolutionSet:
        worst_i = self.__maxheap[0][1]

        return self.__solutions[worst_i]

    def iter_solutions(self) -> Iterator[SolutionSet]:
        for solution in self.__solutions:
            yield solution

    def __try_update_best(self, candidate: SolutionSet) -> bool:
        if self.__best_i is not None and candidate > self.get_best():
            return False

        self.__best_i = self.__last_i

        return True

    def __add_max(self, solution: SolutionSet) -> None:
        """
        Adds a solution to the max heap.

        Time O(log l)
        """
        self.__solutions.append(solution)
        i = len(self.__solutions) - 1
        self.__last_i = i

        # O(log l)
        heapq.heappush(
            self.__maxheap,
            (
                # since heapq implements a min heap only, to have a max heap we must
                # multiply by -1. All values in max heap are negative
                -solution.obj_func,
                self.__last_i,
            ),
        )

    def __update_worst(self, worse: SolutionSet) -> None:
        """
        Time O(log l)
        """
        worst_i = self.__maxheap[0][1]
        self.__solutions[worst_i] = worse
        # new solution is not necessarily the new worst,
        # heap root won't necessarily be last_i
        self.__last_i = worst_i

        # O(log l)
        heapq.heapreplace(
            self.__maxheap,
            (
                -worse.obj_func,
                self.__last_i,
            ),
        )

    def __len__(self) -> int:
        return len(self.__solutions)
