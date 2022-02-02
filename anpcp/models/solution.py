from dataclasses import dataclass, field
from itertools import repeat
import random
import sys
from typing import List, Set, Tuple

from models import Solver

@dataclass
class Solution:
    _solver: Solver = field(repr=False)

    open_facilities: Set[int] = field(init=False, default_factory=set)
    allocations: List[List[int]] = field(init=False, default_factory=list)

    objective_function: int = field(init=False, default=sys.maxsize)
    max_alphath: int = field(init=False, default=-1)
    time: float = field(init=False, repr=False, default=-1)


    def __post_init__(self) -> None:
        self.__init_allocations()
        if self.open_facilities:
            self.__allocate_all()
            if len(self.open_facilities) >= self._solver.alpha:
                self.update_obj_func()


    def set_random(self) -> None:
        self.open_facilities = set(
            random.sample(
                self._solver.instance.facilities_indexes,
                self._solver.p
            )
        )
        self.__allocate_all()
        self.update_obj_func()


    def __init_allocations(self) -> None:
        n = self._solver.instance.n
        m = self._solver.instance.m
        self.allocations = list(repeat(
            list(repeat(0, m)),
            n
        ))


    def __allocate_all(self) -> None:
        alpha = self._solver.alpha
        for customer in self._solver.instance.customers_indexes:
            for kth in (alpha, alpha + 1):
                closest, dist = self.get_kth_closest(customer, kth)
                self.allocate(customer, closest, kth)


    def allocate(self, customer: int, facility: int, kth: int) -> None:
        self.allocations[customer][facility] = kth


    def deallocate(self, customer: int, facility: int) -> None:
        self.allocate(customer, facility, 0)


    def get_kth_closest(self, customer: int, kth: int) -> Tuple[int, int]:
        facility = self.allocations[customer].index(kth)
        distance = self._solver.instance.get_distance(customer, facility)
        return facility, distance


    def get_alphath(self, fromindex: int) -> Tuple[int, int]:
        return self.get_kth_closest(fromindex, self._solver.alpha)


    def eval_obj_func(self) -> Tuple[int, int]:
        return max(
            (
                (f, self._solver.instance.distances[c][f])
                if self.allocations[c][f] == self._solver.alpha else 0
                for c in self._solver.instance.customers_indexes
                for f in self._solver.instance.facilities_indexes
            ),
            key=lambda ad: ad[1],
        )


    def update_obj_func(self) -> None:
        self.max_alphath, self.objective_function = self.eval_obj_func()


    def insert(self, facility: int) -> None:
        self.open_facilities.add(facility)


    def remove(self, facility: int) -> None:
        self.open_facilities.discard(facility)
        for customer in self._solver.instance.customers_indexes:
            self.deallocate(customer, facility)
