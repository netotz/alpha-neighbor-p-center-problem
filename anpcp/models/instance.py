from typing import List, Sequence, Set, Tuple
from random import randint
from itertools import product
from copy import deepcopy

import numpy as np
from scipy import spatial
import tsplib95

from . import Vertex


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
        self.n = len(vertexes)
        self.indexes = {v.index for v in self.vertexes}
        if with_distances:
            coords = [[v.x, v.y] for v in self.vertexes]
            distances = spatial.distance_matrix(coords, coords)
            self.distances = np.array([
                [round(d) for d in row]
                for row in distances
            ])
            self.sorted_dist = [
                sorted(enumerate(row), key=lambda c: c[1])[1:]
                for row in self.distances
            ]
        else:
            self.distances = None


    @classmethod
    def random(cls, n: int, p: int, alpha: int, x_max: int = 1000, y_max: int = 1000) -> 'Instance':
        coords = set()
        while len(coords) < n:
            coords |= {
                (randint(0, x_max), randint(0, y_max))
                for _ in range(n - len(coords))
            }
        return Instance(
            p, alpha,
            [
                Vertex(i, x, y)
                for i, (x, y) in enumerate(coords)
            ]
        )
    

    @classmethod
    def read_from(cls, filename: str, p: int, alpha: int) -> 'Instance':
        problem = tsplib95.load(filename)
        nodes = problem.node_coords if problem.node_coords else problem.display_data
        return Instance(
            p, alpha, [
                Vertex(i - 1, int(x), int(y))
                for i, (x, y) in nodes.items()
            ]
        )


    def get_indexes(self) -> Set[int]:
        return {v.index for v in self.vertexes}


    def get_dist(self, fromindex: int, toindex: int) -> int:
        return self.distances[fromindex][toindex]


    def get_farthest_indexes(self) -> Tuple[int, int]:
        return np.unravel_index(
            self.distances.argmax(),
            self.distances.shape
        )
    

    def get_parameters(self) -> Tuple[int, int, int]:
        return self.n, self.p, self.alpha


def generate_instances(
        amount: int,
        n: int,
        ps: Sequence[int],
        alphas: Sequence[int]) -> List[Instance]:
    instances = list()
    for _ in range(amount):
        base = Instance.random(n, 0, 0)
        for p, alpha in product(ps, alphas):
            instance = deepcopy(base)
            instance.p = p
            instance.alpha = alpha
            instances.append(instance)
    return instances
