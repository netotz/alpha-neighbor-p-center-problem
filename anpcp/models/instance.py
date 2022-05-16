from dataclasses import dataclass, field
import os
from typing import List, Set, Tuple
from random import randint

import numpy as np
from scipy import spatial
import tsplib95

from models.vertex import Vertex


@dataclass
class Instance:
    users: List[Vertex] = field(repr=False)
    facilities: List[Vertex] = field(repr=False)

    users_indexes: Set[int] = field(init=False, default_factory=set, repr=False)
    facilities_indexes: Set[int] = field(init=False, default_factory=set, repr=False)

    n: int = field(init=False)
    m: int = field(init=False)

    distances: List[List[int]] = field(init=False, default_factory=list, repr=False)
    facilities_distances: List[List[int]] = field(init=False, default_factory=list, repr=False)
    sorted_distances: List[List[int]] = field(
        init=False, default_factory=list, repr=False
    )

    def __post_init__(self) -> None:
        self.n = len(self.users)
        self.m = len(self.facilities)

        self.users_indexes = {u.index for u in self.users}
        self.facilities_indexes = {f.index for f in self.facilities}

        users_coords = [[u.x, u.y] for u in self.users]
        facilities_coords = [[f.x, f.y] for f in self.facilities]

        self.distances = [
            [round(d) for d in row]
            for row in spatial.distance_matrix(users_coords, facilities_coords)
        ]
        self.sorted_distances = [
            sorted(enumerate(row), key=lambda c: c[1]) for row in self.distances
        ]

        self.facilities_distances = [
            [round(d) for d in row]
            for row in spatial.distance_matrix(facilities_coords, facilities_coords)
        ]

    @classmethod
    def random(cls, n: int, m: int, x_max: int = 1000, y_max: int = 1000) -> "Instance":
        distinct_coords = set()
        total = n + m

        while len(distinct_coords) < total:
            distinct_coords |= {
                (randint(0, x_max), randint(0, y_max))
                for _ in range(total - len(distinct_coords))
            }

        distinct_coords = list(distinct_coords)

        # each list has its own enumeration
        users = [Vertex(i, x, y) for i, (x, y) in enumerate(distinct_coords[:n])]
        facilities = [Vertex(i, x, y) for i, (x, y) in enumerate(distinct_coords[n:])]

        return Instance(users, facilities)

    @classmethod
    def read(cls, filename: str) -> "Instance":
        """
        ! Deprecated
        """
        problem = tsplib95.load(filename)
        nodes = problem.node_coords if problem.node_coords else problem.display_data
        return Instance([Vertex(i - 1, int(x), int(y)) for i, (x, y) in nodes.items()])

    def write(self, directory: str, id: int = 1) -> None:
        """
        ! Deprecated
        """
        filename = f"anpcp{self.n}_{id}.tsp"
        filepath = os.path.join(directory, filename)
        with open(filepath, "w") as file:
            file.write(f"NAME: {filename}\n")
            file.write("TYPE: ANPCP\n")
            file.write(f"DIMENSION: {self.n}\n")
            file.write("EDGE_WEIGHT_TYPE: EUC_2D\n")
            file.write("NODE_COORD_SECTION\n")
            for v in self.vertexes:
                file.write(f"{v.index + 1} {v.x} {v.y}\n")
            file.write("EOF\n")

    def get_distance(self, from_user: int, to_facility: int) -> int:
        return self.distances[from_user][to_facility]

    def get_farthest_indexes(self) -> Tuple[int, int]:
        return np.unravel_index(self.distances.argmax(), self.distances.shape)
