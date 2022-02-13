from dataclasses import dataclass


@dataclass
class AllocatedFacility:
    '''
    Data class designed to wrap a facility `index`,
    its allocated `customer`, and their `distance`.

    This object only replaces the need to use a tuple[int, int].
    '''
    index: int
    customer: int
    distance: int
