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


    def distance_to(self, point: 'Vertex') -> float:
        return math.dist(self.to_tuple(), point.to_tuple())
