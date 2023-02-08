from dataclasses import dataclass


@dataclass
class AllocatedFacility:
    """
    Wraps a facility `index`, its allocated `customer`, and the `distance` between them.

    This class replaces a `tuple[int, int, int]` type.
    """

    index: int
    user: int
    distance: int
