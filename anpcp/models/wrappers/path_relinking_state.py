from dataclasses import dataclass


@dataclass
class PathRelinkingState:
    """
    Wraps properties of local search algorithms.
    """

    candidates_out: set[int] | None = None
    """
    Set of candidate facilities to remove from S.
    If Path Relinking, these are the open facilities in the starting solution
    but not in the target one, S_s - S_t.
    Otherwise, it is the whole set of open facilities, S.
    """

    candidates_in: set[int] | None = None
    """
    Set of candidate facilities to insert into S.
    If Path Relinking, these are the open facilities in the target solution
    but not in the starting one, S_t - S_s.
    Otherwise, it is the whole set of closed facilities, F - S.
    """

    is_running: bool = False
    """
    `True` if Path Relinking is currently running.
    Otherwise, `False`.
    """

    def are_there_candidates(self) -> bool:
        """
        Returns whether or not there are more than 1 available candidates to be swapped.
        """
        return len(self.candidates_in) > 1

    def run(self, candidates_out: set[int], candidates_in: set[int]) -> None:
        self.__update(True, candidates_out, candidates_in)

    def stop(self) -> None:
        self.__update(False, None, None)

    def update_candidates(self, inserted: int, removed: int) -> None:
        """
        Removes `inserted` from `candidates_in` and `removed` from `candidates_out`.

        Call this method after an applied swap during Path Relinking.
        """
        self.candidates_in.remove(inserted)
        self.candidates_out.remove(removed)

    def __update(
        self,
        is_running: bool,
        candidates_out: set[int] | None,
        candidates_in: set[int] | None,
    ) -> None:
        self.is_running = is_running
        self.candidates_out = candidates_out
        self.candidates_in = candidates_in
