from dataclasses import dataclass
from warnings import warn


class UnexpectedUpdateWarning(UserWarning):
    pass


@dataclass
class LocalSearchState:
    """
    Wraps properties of local search algorithms.
    """

    candidates_out: set[int]
    """
    Set of candidate facilities to remove from S.
    If Path Relinking, these are the open facilities in the starting solution
    but not in the target one, S_s - S_t.
    Otherwise, it is the whole set of open facilities, S.
    """

    candidates_in: set[int]
    """
    Set of candidate facilities to insert into S.
    If Path Relinking, these are the open facilities in the target solution
    but not in the starting one, S_t - S_s.
    Otherwise, it is the whole set of closed facilities, F - S.
    """

    is_path_relinking: bool = False
    """
    `True` if Path Relinking is currently being applied.
    Otherwise, `False`.
    """

    def are_there_candidates(self) -> bool:
        """
        Returns whether or not there are more than 1 available candidates to be swapped.
        """
        return len(self.candidates_in) > 1

    def start_path_relinking(
        self, candidates_out: set[int], candidates_in: set[int]
    ) -> None:
        self.__modify_path_relinking(True, candidates_out, candidates_in)

    def end_path_relinking(
        self, open_facilities: set[int], closed_facilities: set[int]
    ) -> None:
        self.__modify_path_relinking(False, open_facilities, closed_facilities)

    def update_candidates(
        self, open_facilities: set[int], closed_facilities: set[int]
    ) -> None:
        """
        Updates `self.candidates_out = open_facilities` (S) and `self.candidates_in = closed_facilities` (F - S).
        This should be called after an applied swap in S.
        If called during Path Relinking, a `UnexpectedUpdateWarning` is issued.
        """
        if self.is_path_relinking:
            warn(
                "Candidate facilities are trying to be updated during Path Relinking."
                + "This could lead to unexpected behaviour and exceptions."
                + "If you want to end Path Relinking and switch to normal local search, use `end_path_relinking` method instead.",
                UnexpectedUpdateWarning,
            )

        self.__modify_path_relinking(False, open_facilities, closed_facilities)

    def remove_applied_candidates(self, inserted: int, removed: int) -> None:
        self.candidates_in.remove(inserted)
        self.candidates_out.remove(removed)

    def __modify_path_relinking(
        self, is_it: bool, candidates_out: set[int], candidates_in: set[int]
    ) -> None:
        self.is_path_relinking = is_it
        self.candidates_out = candidates_out
        self.candidates_in = candidates_in
