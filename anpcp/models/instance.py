from dataclasses import dataclass
from typing import List, Optional
from random import randint

import numpy as np
from scipy import spatial

from .point import Point

@dataclass
class Instance:
    p: int
    alpha: int
    points: List[Point]
    distances: Optional[np.ndarray] = None
    
    
    def calculate_distances(self) -> None:
        distances = spatial.distance_matrix(
            [[p.x, p.y] for p in self.points],
            [[p.x, p.y] for p in self.points],
        )
        self.distances = np.array([
            [round(d) for d in row]
            for row in distances
        ])


    @classmethod
    def random(cls, n: int, p: int, alpha: int, x_max: int, y_max: int) -> 'Instance':
        coords = set()
        while len(coords) < n:
            coords |= set(
                (randint(0, x_max), randint(0, y_max))
                for _ in range(n - len(coords))
            )
        points = [Point(i, x, y) for i, (x, y) in enumerate(coords)]
        return Instance(p, alpha, points)
