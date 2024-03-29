from .instance_same_set import InstanceSameSet
from .solver import Solver


class SolverSameSet(Solver):
    def __init__(
        self,
        instance: InstanceSameSet,
        p: int,
        alpha: int,
        with_random_solution=False,
        is_first_improvement=True,
        seed: int | None = None,
    ):
        super().__init__(
            instance, p, alpha, with_random_solution, is_first_improvement, seed
        )

    def get_users_indexes(self) -> set[int]:
        """
        Returns the indexes of closed facilities since U and F
        are the same set of points.
        """
        return self.solution.closed_facilities
