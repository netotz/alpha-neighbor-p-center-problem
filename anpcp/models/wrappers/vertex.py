from dataclasses import dataclass
from enum import IntEnum
import math


class VertexType(IntEnum):
    USER = 0
    FACILITY = 1


@dataclass
class Vertex:
    index: int
    x: int
    y: int

    def __init__(self, index: int, x: int, y: int):
        self.index = index
        self.x = x
        self.y = y

    def to_tuple(self) -> tuple[int, int]:
        return self.x, self.y

    def distance_to(self, vertex: "Vertex") -> float:
        return math.dist(self.to_tuple(), vertex.to_tuple())
