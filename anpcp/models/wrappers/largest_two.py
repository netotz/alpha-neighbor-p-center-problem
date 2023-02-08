from .moved_facility import MovedFacility


class LargestTwo:
    """
    Wraps the largest two facilities from a data structure by their radius.
    """

    def __init__(self) -> "LargestTwo":
        self.first = MovedFacility(-1, 0)
        self.second = MovedFacility(-1, 0)

    def try_update(self, facility_index: int, radius: int):
        """
        Replaces any of the largest two if `facility_index` has the appropriate `radius`.
        """
        did_update = False

        if radius > self.first.radius:
            self.second = self.first
            self.first = MovedFacility(facility_index, radius)
            did_update = True
        elif radius > self.second.radius:
            self.second = MovedFacility(facility_index, radius)
            did_update = True

        return did_update
