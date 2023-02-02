from collections import deque
from dataclasses import dataclass


@dataclass
class TabuRecency:
    """
    Short term or recency based memory for intensification
    in tabu search.
    """

    size: int

    def __post_init__(self):
        self.__queue = deque[int]()
        self.__set = set[int]()

    def is_tabu(self, facility: int) -> bool:
        return facility in self.__set

    def mark(self, facility: int) -> None:
        if len(self.__queue) == self.size:
            nontabu = self.__queue.popleft()
            self.__set.remove(nontabu)

        self.__queue.append(facility)
        self.__set.add(facility)
