from dataclasses import dataclass


@dataclass
class ProfitableSwap:
    facility_in: int
    facility_out: int
    profit: int
