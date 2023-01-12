from dataclasses import dataclass

from models.instance_same_set import InstanceSameSet
from models.solver import Solver


@dataclass
class SolverSameSet(Solver):
    instance: InstanceSameSet

    def get_users_indexes(self) -> set[int]:
        """
        Returns the indexes of closed facilities since U and F
        are the same set of points.
        """
        return self.solution.closed_facilities
