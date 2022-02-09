from dataclasses import dataclass


@dataclass
class AllocatedFacility:
    '''
    Data class designed to wrap a facility `index` and the `distance` to its allocated customer.

    This object only replaces the need to use a tuple[int, int].
    '''
    index: int
    distance: int
