import heapq

from .solution_set import SolutionSet


class EliteDifferencesHeap:
    def __init__(
        self,
        candidate: SolutionSet,
        current_pool: list[SolutionSet],
        min_symmetric_diff: int,
    ) -> None:
        """
        Time O(pl)
        """
        self.is_symmetrically_different = True

        self.__heap: list[tuple[int, int, int]] = []

        ## O(pl)
        # O(l)
        for i, elite in enumerate(current_pool):
            # O(p)
            symmetric_diff = len(elite.open_facilities ^ candidate.open_facilities)

            if symmetric_diff < min_symmetric_diff:
                self.is_symmetrically_different = False

                return

            obj_func_diff = elite.obj_func - candidate.obj_func

            # obj_func_diff is negative because Python heap is min
            self.__heap.append(
                (
                    symmetric_diff,
                    -obj_func_diff,
                    i,
                )
            )

        # O(l)
        heapq.heapify(self.__heap)

    def get_index_to_replace(self) -> int:
        return self.__heap[0][2]
