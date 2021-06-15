from dataclasses import dataclass
from typing import List, Optional, Tuple
from random import randint

import numpy as np
from scipy import spatial

from .vertex import Vertex

@dataclass
class Instance:
    p: int
    alpha: int
    points: List[Vertex]
    distances: Optional[np.ndarray] = None


    @classmethod
    def random(cls, n: int, p: int, alpha: int, x_max: int, y_max: int) -> 'Instance':
        coords = set()
        while len(coords) < n:
            coords |= set(
                (randint(0, x_max), randint(0, y_max))
                for _ in range(n - len(coords))
            )
        points = [Vertex(i + 1, x, y) for i, (x, y) in enumerate(coords)]
        return Instance(p, alpha, points)


    def calculate_distances(self) -> None:
        distances = spatial.distance_matrix(
            [[p.x, p.y] for p in self.points],
            [[p.x, p.y] for p in self.points],
        )
        self.distances = np.array([
            [round(d) for d in row]
            for row in distances
        ])


    def get_dist(self, fromindex: int, toindex: int) -> int:
        return self.distances[fromindex - 1][toindex - 1]


    def get_farthest_indexes(self) -> Tuple[int, int]:
        return np.unravel_index(
            self.distances.argmax(),
            self.distances.shape
        )
