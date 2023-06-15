import numpy as np
import numpy.typing as npt

from .wrappers import AllocatedFacility


class Solution:
    def __init__(self):
        self.open_facilities: set[int] = set()
        self.closed_facilities: set[int] = set()
        self.allocations: npt.NDArray[np.ubyte] | None = None

        self.critical_allocation: AllocatedFacility | None = None
        self.time = -1.0
        self.moves = -1
        self.last_improvement = -1

    def __repr__(self) -> str:
        return f"{Solution.__name__}(critical={self.critical_allocation}, open={self.open_facilities}, time={self.time}, moves={self.moves})"

    def get_obj_func(self) -> int:
        """
        Gets the ANPCP objective function of this solution
        by accessing the `critical_allocation` field
        (not by calculating it).
        """
        return self.critical_allocation.distance

    def insert(self, facility: int) -> None:
        self.closed_facilities.discard(facility)
        self.open_facilities.add(facility)

    def remove(self, facility: int) -> None:
        self.open_facilities.discard(facility)
        self.closed_facilities.add(facility)

    def swap(self, facility_in: int, facility_out: int) -> None:
        """
        Applies a swap to the solution by inserting `facility_in` to it
        and removing `facility_out` from it.
        """
        self.insert(facility_in)
        self.remove(facility_out)
