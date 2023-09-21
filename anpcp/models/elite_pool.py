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
        self.__open_sets: set[frozenset[int]] = set()
        """
        Set of open facilities' sets from `__solutions` to avoid duplicated solutions.
        """

        self.__last_i = 0
        """
        Index in `__solutions` of last inserted or updated solution.
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

        Time O(p + log l)
        """
        # avoid duplicated solutions
        if solution.open_facilities in self.__open_sets:
            return False

        is_added = False

        if len(self) < self.limit:
            # O(p + log l)
            self.__add_max(solution)
            is_added = True
        elif solution < self.get_worst():
            # O(p + log l)
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

    def __add_solution(self, new: SolutionSet) -> None:
        """
        Adds `solution` to inner list and its open facilities to inner set,
        and updates `self.__last_i`.

        Time O(p) to hash
        """
        # O(p) to hash
        self.__open_sets.add(new.open_facilities)

        self.__solutions.append(new)
        self.__last_i = len(self.__solutions) - 1

    def __replace_solution(self, new: SolutionSet, index: int) -> None:
        """
        Replaces the solution at `index` with `new`, removes replaced from inner set and
        adds the open facilities of `new`, and updates `self.__last_i = index`.

        Time O(p) to hash
        """
        replaced = self.__solutions[index]
        self.__open_sets.remove(replaced.open_facilities)
        # O(p) to hash
        self.__open_sets.add(new.open_facilities)

        self.__solutions[index] = new
        self.__last_i = index

    def __try_update_best(self, candidate: SolutionSet) -> bool:
        if self.__best_i is not None and candidate > self.get_best():
            return False

        self.__best_i = self.__last_i

        return True

    def __add_max(self, solution: SolutionSet) -> None:
        """
        Adds a solution to the max heap.

        Time O(p + log l)
        """
        # O(p)
        self.__add_solution(solution)

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

    def __update_worst(self, better: SolutionSet) -> None:
        """
        Time O(p + log l)
        """
        worst_i = self.__maxheap[0][1]
        # O(p)
        self.__replace_solution(better, worst_i)

        # O(log l)
        heapq.heapreplace(
            self.__maxheap,
            (
                -better.obj_func,
                self.__last_i,
            ),
        )

    def __len__(self) -> int:
        return len(self.__solutions)
