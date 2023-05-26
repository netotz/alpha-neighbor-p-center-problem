from typing import Tuple
import math

USER = 0
FACILITY = 1


class Vertex:
    def __init__(self, index: int, x: int, y: int):
        self.index = index
        self.x = x
        self.y = y

    def to_tuple(self) -> Tuple[int, int]:
        return self.x, self.y

    def distance_to(self, vertex: "Vertex") -> float:
        return math.dist(self.to_tuple(), vertex.to_tuple())
