from dataclasses import dataclass
from anpcp.models.solver import Solver


@dataclass
class SolverSameSet(Solver):
    def get_users_indexes(self) -> set[int]:
        """
        Returns the indexes of closed facilities since U and F
        are the same set of points.
        """
        return self.solution.closed_facilities
