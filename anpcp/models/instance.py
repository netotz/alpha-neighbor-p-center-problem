from dataclasses import dataclass, field
import os
from typing import List, Set, Tuple
from random import randint

import numpy as np
from scipy import spatial
import tsplib95

from . import Vertex


@dataclass
class Instance:
    vertexes: List[Vertex] = field(repr=False)
    n: int = field(init=False)
    indexes: Set[int] = field(init=False, default=None, repr=False)
    distances: np.ndarray = field(init=False, default=None, repr=False)
    sorted_dist: np.ndarray = field(init=False, default=None, repr=False)


    def __post_init__(self) -> None:
        self.n = len(self.vertexes)
        self.indexes = {v.index for v in self.vertexes}

        coords = [[v.x, v.y] for v in self.vertexes]
        self.distances = np.array([
            [round(d) for d in row]
            for row in spatial.distance_matrix(coords, coords)
        ])
        self.sorted_dist = [
            sorted(enumerate(row), key=lambda c: c[1])[1:]
            for row in self.distances
        ]


    @classmethod
    def random(cls, n: int, x_max: int = 1000, y_max: int = 1000) -> 'Instance':
        coords = set()
        while len(coords) < n:
            coords |= {
                (randint(0, x_max), randint(0, y_max))
                for _ in range(n - len(coords))
            }
        return Instance([
            Vertex(i, x, y)
            for i, (x, y) in enumerate(coords)
        ])


    @classmethod
    def read(cls, filename: str) -> 'Instance':
        problem = tsplib95.load(filename)
        nodes = problem.node_coords if problem.node_coords else problem.display_data
        return Instance([
            Vertex(i - 1, int(x), int(y))
            for i, (x, y) in nodes.items()
        ])


    def write(self, directory: str, id: int = 1) -> None:
        filename = f'anpcp{self.n}_{id}.tsp'
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w') as file:
            file.write(f'NAME: {filename}\n')
            file.write('TYPE: ANPCP\n')
            file.write(f'DIMENSION: {self.n}\n')
            file.write('EDGE_WEIGHT_TYPE: EUC_2D\n')
            file.write('NODE_COORD_SECTION\n')
            for v in self.vertexes:
                file.write(f'{v.index + 1} {v.x} {v.y}\n')
            file.write('EOF\n')


    def get_dist(self, fromindex: int, toindex: int) -> int:
        return self.distances[fromindex][toindex]


    def get_farthest_indexes(self) -> Tuple[int, int]:
        return np.unravel_index(
            self.distances.argmax(),
            self.distances.shape
        )
