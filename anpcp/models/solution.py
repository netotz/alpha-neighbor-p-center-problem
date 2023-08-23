class Solution:
    def __init__(self):
        self.obj_func: int = -1
        self.open_facilities: set[int] = set()
        self.closed_facilities: set[int] = set()

        self.time = -1.0
        self.moves = -1
        self.last_improvement = -1

    def __repr__(self) -> str:
        return f"{Solution.__name__}(x(S)={self.obj_func}, S={self.open_facilities}, time={self.time}, moves={self.moves})"

    def insert(self, facility: int) -> None:
        self.closed_facilities.discard(facility)
        self.open_facilities.add(facility)

    def remove(self, facility: int) -> None:
        self.open_facilities.discard(facility)
        self.closed_facilities.add(facility)

    def swap(self, facility_in: int, facility_out: int) -> None:
        """
        Applies a swap to the solution by inserting `facility_in` to it
        and removing `facility_out` from it.
        """
        self.insert(facility_in)
        self.remove(facility_out)
