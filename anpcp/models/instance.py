from dataclasses import dataclass, field
import json
import os
from typing import List, Set, Tuple
from random import randint

from scipy import spatial
import tsplib95

from models.vertex import Vertex


@dataclass
class Instance:
    facilities: List[Vertex] = field(repr=False)
    users: List[Vertex] = field(repr=False)

    users_indexes: Set[int] = field(init=False, default_factory=set, repr=False)
    facilities_indexes: Set[int] = field(init=False, default_factory=set, repr=False)

    m: int = field(init=False)
    n: int = field(init=False)

    distances: List[List[int]] = field(init=False, default_factory=list, repr=False)
    sorted_distances: List[List[int]] = field(
        init=False, default_factory=list, repr=False
    )

    facilities_distances: List[List[int]] = field(
        init=False, default_factory=list, repr=False
    )
    # farthests: Tuple[int, int] = field(init=False, default_factory=tuple, repr=False)

    def __post_init__(self) -> None:
        self.m = len(self.users)
        self.n = len(self.facilities)

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
        # self.farthests = self.get_farthest_indexes()

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
        facilities = [Vertex(i, x, y) for i, (x, y) in enumerate(distinct_coords[:n])]
        users = [Vertex(i, x, y) for i, (x, y) in enumerate(distinct_coords[n:])]

        return Instance(facilities, users)

    @classmethod
    def read(cls, filename: str) -> "Instance":
        """
        ! Deprecated
        """
        problem = tsplib95.load(filename)
        nodes = problem.node_coords if problem.node_coords else problem.display_data
        return Instance([Vertex(i - 1, int(x), int(y)) for i, (x, y) in nodes.items()])

    def write_json(self, directory: str, id: int) -> None:
        """ """
        data = {
            "n": self.n,
            "m": self.m,
            "facilities": [{"i": f.index, "x": f.x, "y": f.y} for f in self.facilities],
            "users": [{"i": u.index, "x": u.x, "y": u.y} for u in self.users],
            "distances": self.distances,
            "facilities_distances": self.facilities_distances,
        }
        filename = f"anpcp_{self.n}_{self.m}_{id}.json"
        path = os.path.join(directory, filename)

        with open(path, "w") as jsonfile:
            json.dump(data, jsonfile)

    def get_distance(self, from_user: int, to_facility: int) -> int:
        return self.distances[from_user][to_facility]

    def get_farthest_indexes(self) -> Tuple[int, int]:
        """
        Time O(m**2)
        """
        _, fi, fj = max(
            (
                (self.facilities_distances[i][j], i, j)
                for i in range(self.n)
                for j in range(self.n)
            ),
            key=lambda t: t[0],
        )

        return fi, fj
