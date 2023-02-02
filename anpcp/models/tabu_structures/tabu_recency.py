from collections import deque
from dataclasses import dataclass


@dataclass
class TabuRecency:
    """
    Short term or recency based memory for intensification in tabu search.

    It's implemented with a queue of size `size` that stores tabu active facilities,
    and with a set that stores the same facilities to check in O(1) if any of them is tabu.
    """

    size: int

    def __post_init__(self):
        self.__queue = deque[int]()
        self.__set = set[int]()

    def is_tabu(self, facility: int) -> bool:
        """
        Checks if `facility` is currently tabu active.
        """
        return facility in self.__set

    def mark(self, facility: int) -> None:
        """
        Marks `facility` as tabu active.
        """
        self.__queue.append(facility)
        self.__set.add(facility)

        self.__fix_queue()

    def __fix_queue(self) -> None:
        """
        Private method to fix interal queue by dequeing until its size equals `size`.
        """
        while len(self.__queue) > self.size:
            self.__dequeue()

    def __dequeue(self) -> None:
        """
        Private method to dequeue the oldest facility and remove it from the set.
        """
        nontabu = self.__queue.popleft()
        self.__set.remove(nontabu)
