from dataclasses import dataclass
from typing import List, Set, Tuple
from random import randint

import numpy as np
from scipy import spatial

from .vertex import Vertex

@dataclass
class Instance:
    def __init__(
            self,
            p: int,
            alpha: int,
            vertexes: List[Vertex],
            with_distances: bool = True) -> None:
        self.p = p
        self.alpha = alpha
        self.vertexes = vertexes
        self.indexes = {v.index for v in self.vertexes}
        if with_distances:
            coords = [[v.x, v.y] for v in self.vertexes]
            distances = spatial.distance_matrix(coords, coords)
            self.distances = np.array([
                [round(d) for d in row]
                for row in distances
            ])
        else:
            self.distances = None


    @classmethod
    def random(cls, n: int, p: int, alpha: int, x_max: int, y_max: int) -> 'Instance':
        coords = set()
        while len(coords) < n:
            coords |= {
                (randint(0, x_max), randint(0, y_max))
                for _ in range(n - len(coords))
            }
        return Instance(
            p, alpha,
            [Vertex(i + 1, x, y) for i, (x, y) in enumerate(coords)]
        )


    def get_indexes(self) -> Set[int]:
        return {v.index for v in self.vertexes}


    def get_dist(self, fromindex: int, toindex: int) -> int:
        return self.distances[fromindex - 1][toindex - 1]


    def get_farthest_indexes(self) -> Tuple[int, int]:
        return np.unravel_index(
            self.distances.argmax(),
            self.distances.shape
        )
