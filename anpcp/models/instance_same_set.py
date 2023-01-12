from dataclasses import dataclass
import math

from models.vertex import Vertex
from models.instance import Instance, read_node_coords


@dataclass
class InstanceSameSet(Instance):
    @classmethod
    def read_tsp(cls, filepath: str) -> "InstanceSameSet":
        """ """
        nodes = [Vertex(i - 1, x, y) for i, x, y in read_node_coords(filepath)]
        return cls(nodes, nodes)

    def get_distance(self, from_user: int, to_facility: int) -> int:
        dist = self.distances[from_user][to_facility]

        # if f and u are same point (d=0), skip fi by returning infinity
        if from_user == to_facility:
            assert dist == 0
            return math.inf

        return dist
