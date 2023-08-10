from dataclasses import dataclass


@dataclass
class BestMove:
    """
    Wrapper of the best facility to insert, the best facility to remove,
    and the resulting radius of their swap found by the A-FVS algorithm.
    """

    fi: int
    """
    Index of the facility to insert.
    """
    fr: int
    """
    Index of the facility to remove.
    """
    radius: int
    """
    Resulting objective function of S after swapping `fi` and `fr`.
    """
