from dataclasses import dataclass


@dataclass
class AllocatedFacility:
    '''
    Class that wraps a facility index and the distance to its allocated customer.

    This object replaces the need to use a tuple[int, int].
    '''
    index: int
    distance: int
