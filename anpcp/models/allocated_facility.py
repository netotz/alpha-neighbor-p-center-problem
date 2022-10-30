from dataclasses import dataclass


@dataclass
class AllocatedFacility:
    """
    Wraps a facility `index`, its allocated `customer`, and their `distance`.
    These 3 attributes are `int`.

    This class replaces the need to use a `tuple[int, int]`.
    """

    index: int
    user: int
    distance: int
