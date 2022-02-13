from dataclasses import dataclass, field
from typing import List, Set

from models.allocated_facility import AllocatedFacility


@dataclass
class Solution:
    open_facilities: Set[int] = field(init=False, default_factory=set)
    closed_facilities: Set[int] = field(init=False, repr=False, default_factory=set)
    allocations: List[List[int]] = field(init=False, repr=False, default_factory=list)

    critical_allocation: AllocatedFacility = field(init=False, default=None)
    time: float = field(init=False, repr=False, default=-1)


    def get_objective_function(self) -> int:
        '''
        Gets the ANPCP objective function of this solution
        by accessing the critical allocation (not by calculating it).
        '''
        return self.critical_allocation.distance
