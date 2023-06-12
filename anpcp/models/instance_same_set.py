import math
from typing import List

from .wrappers import Vertex
from .instance import Instance, read_node_coords


class InstanceSameSet(Instance):
    def __init__(
        self, facilities: List[Vertex], users: List[Vertex], name="", index=-1
    ):
        super().__init__(facilities, users, name, index)

    @classmethod
    def read_tsp(cls, filepath: str) -> "InstanceSameSet":
        """
        Reads a TSP Lib file (.tsp).

        The same set of nodes is used for both users and facilities.
        """
        nodes = [Vertex(i - 1, x, y) for i, x, y in read_node_coords(filepath)]
        return cls(nodes, nodes)

    def get_distance(self, from_user: int, to_facility: int) -> int:
        dist = self.distances[from_user][to_facility]

        # if f and u are same point (d=0), skip fi by returning infinity
        if from_user == to_facility:
            return math.inf

        return dist
