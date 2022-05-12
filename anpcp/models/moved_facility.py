from dataclasses import dataclass


@dataclass
class MovedFacility:
    """
    Represents a facility `index` and its `radius`,
    according to the min-max fast swap algorithm.
    """

    index: int
    radius: int
