from dataclasses import dataclass, field
import sys
from typing import List, Set


@dataclass
class Solution:
    open_facilities: Set[int] = field(init=False, default_factory=set)
    allocations: List[List[int]] = field(init=False, repr=False, default_factory=list)

    objective_function: int = field(init=False, default=sys.maxsize)
    max_alphath: int = field(init=False, default=-1)
    time: float = field(init=False, repr=False, default=-1)
