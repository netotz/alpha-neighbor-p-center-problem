from dataclasses import dataclass
from typing import Tuple
import math


@dataclass
class Vertex:
    index: int
    x: int
    y: int


    def to_tuple(self) -> Tuple[int, int]:
        return self.x, self.y


    def distance_to(self, vertex: 'Vertex') -> float:
        return math.dist(self.to_tuple(), vertex.to_tuple())
