from dataclasses import dataclass, field
from typing import List, Set

from models.wrappers import AllocatedFacility


@dataclass
class Solution:
    open_facilities: Set[int] = field(init=False, default_factory=set)
    closed_facilities: Set[int] = field(init=False, repr=False, default_factory=set)
    allocations: List[List[int]] = field(init=False, repr=False, default_factory=list)

    critical_allocation: AllocatedFacility = field(init=False, default=None)
    time: float = field(init=False, repr=False, default=-1)
    moves: int = field(init=False, repr=False, default=-1)
    last_improvement: int = field(init=False, repr=False, default=-1)

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
