from dataclasses import dataclass, field
import json
import os
from typing import List, Optional, Set, Tuple

from scipy import spatial
import numpy as np

from models.vertex import VertexType, Vertex


@dataclass
class Instance:
    facilities: List[Vertex] = field(repr=False)
    users: List[Vertex] = field(repr=False)
    name: str = ""
    index: int = -1

    users_indexes: Set[int] = field(init=False, default_factory=set, repr=False)
    facilities_indexes: Set[int] = field(init=False, default_factory=set, repr=False)

    n: int = field(init=False)
    m: int = field(init=False)

    distances: List[List[int]] = field(default_factory=list, repr=False)
    sorted_distances: List[List[int]] = field(
        init=False, default_factory=list, repr=False
    )

    facilities_distances: List[List[int]] = field(default_factory=list, repr=False)
    # farthests: Tuple[int, int] = field(init=False, default_factory=tuple, repr=False)

    def __post_init__(self) -> None:
        self.n = len(self.users)
        self.m = len(self.facilities)

        self.users_indexes = {u.index for u in self.users}
        self.facilities_indexes = {f.index for f in self.facilities}

        users_coords = [[u.x, u.y] for u in self.users]
        facilities_coords = [[f.x, f.y] for f in self.facilities]

        if not self.distances:
            self.distances = [
                [round(d) for d in row]
                for row in spatial.distance_matrix(users_coords, facilities_coords)
            ]
        self.sorted_distances = [
            sorted(enumerate(row), key=lambda c: c[1]) for row in self.distances
        ]

        if not self.facilities_distances:
            self.facilities_distances = [
                [round(d) for d in row]
                for row in spatial.distance_matrix(facilities_coords, facilities_coords)
            ]
        # self.farthests = self.get_farthest_indexes()

    @classmethod
    def random(
        cls,
        n: int,
        m: int,
        x_max: int = 1000,
        y_max: int = 1000,
        seed: Optional[int] = None,
    ) -> "Instance":
        distinct_coords = set()
        total = n + m

        # use seeded random generator for reproducibility
        rng = np.random.default_rng(seed)

        while len(distinct_coords) < total:
            distinct_coords |= {
                (
                    rng.integers(x_max, endpoint=True).item(),
                    rng.integers(y_max, endpoint=True).item(),
                )
                for _ in range(total - len(distinct_coords))
            }

        distinct_coords = list(distinct_coords)

        # each list has its own enumeration
        facilities = [Vertex(i, x, y) for i, (x, y) in enumerate(distinct_coords[:m])]
        users = [Vertex(i, x, y) for i, (x, y) in enumerate(distinct_coords[m:])]

        return cls(facilities, users)

    @classmethod
    def read(cls, filepath: str) -> "Instance":
        filename = os.path.basename(filepath)

        instance = (
            cls.read_json(filepath)
            if filename.startswith("anpcp_")
            else cls.read_tsp(filepath)
        )

        name = filename.split(".")[0]
        index = name.split("_")[-1]

        instance.name = name
        instance.index = index

        return instance

    @classmethod
    def read_json(cls, filepath: str) -> "Instance":
        """
        Reads an instance JSON file and loads its data.
        """
        with open(filepath, "r") as jsonfile:
            data = json.load(jsonfile)

        try:
            return cls(
                [Vertex(f["i"], f["x"], f["y"]) for f in data["facilities"]],
                [Vertex(u["i"], u["x"], u["y"]) for u in data["users"]],
            )
        except json.JSONDecodeError as error:
            print("The input file has an incorrect format.")
            print(error)

    def write_json(self, directory: str, id: int) -> None:
        """
        Writes instance data to a JSON file.
        """
        data = {
            "m": self.m,
            "n": self.n,
            "facilities": [{"i": f.index, "x": f.x, "y": f.y} for f in self.facilities],
            "users": [{"i": u.index, "x": u.x, "y": u.y} for u in self.users],
        }
        filename = f"anpcp_{self.n}_{self.m}_{id}.json"
        path = os.path.join(directory, filename)

        with open(path, "w") as jsonfile:
            json.dump(data, jsonfile)

    @classmethod
    def read_tsp(cls, filepath: str) -> "Instance":
        """
        Reads a modified instance of the TSP Lib (extension .anpcp.tsp).

        The original indexes of the nodes are lost
        because `Solver` uses a matrix of distances
        whose indexes must be ranges starting at 0.
        """
        facilities = list()
        users = list()
        i = j = 0
        for _, x, y, t in read_node_coords(filepath):
            if t == VertexType.USER:
                users.append(Vertex(i, x, y))
                i += 1
            elif t == VertexType.FACILITY:
                facilities.append(Vertex(j, x, y))
                j += 1

        return cls(facilities, users)

    def get_distance(self, from_user: int, to_facility: int) -> int:
        return self.distances[from_user][to_facility]

    def get_farthest_indexes(self) -> Tuple[int, int]:
        """
        Time O(m**2)
        """
        _, fi, fj = max(
            (
                (self.facilities_distances[i][j], i, j)
                for i in range(self.m)
                for j in range(self.m)
            ),
            key=lambda t: t[0],
        )

        return fi, fj


def read_node_coords(filepath: str) -> List[List[int]]:
    """
    Returns node coords as list of lists,
    where each node has format [index, x, y, type].
    """
    lines = list()
    with open(filepath, "r") as file:
        lines = file.read().split("\n")

    # find index where coords start
    i = 1
    for line in lines:
        if line.startswith("NODE_COORD_SECTION"):
            break
        i += 1

    # trim last index as it's EOF
    nodes = lines[i:-1]
    # each node is a string "i x y t"
    # so split it and convert them to ints
    return [[int(float(value)) for value in node.split()] for node in nodes]
