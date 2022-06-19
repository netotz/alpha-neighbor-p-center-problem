import os
import random

import tsplib95

from models.vertex import VertexType


def split_instance(filename: str, percentage: float):
    """
    Reads an instance from TSP Lib and splits it in 2 sets of facilities and users.

    The number of facilities will be `percentage` of the instance size.
    """
    dirpath = "..\\data"
    filepath = os.path.join(dirpath, filename)

    instance = tsplib95.load(filepath)
    # get number of facilities
    m = int(instance.dimension * percentage)
    # choose indexes to be facilities
    facilities_indexes = set(random.sample(range(1, instance.dimension + 1), m))

    instance.comment += f". FACILITY = {VertexType.FACILITY}, USER = {VertexType.USER}"

    for node in instance.node_coords:
        node_type = (
            VertexType.FACILITY if node in facilities_indexes else VertexType.USER
        )
        # add type at the end of line
        instance.node_coords[node].append(node_type.value)

    # check last index used for this instance
    i = 0
    while os.path.exists(os.path.join(dirpath, f"{instance.name}_{m}_{i}.anpcp.tsp")):
        i += 1

    instance.save(os.path.join(dirpath, f"{instance.name}_{m}_{i}.anpcp.tsp"))
