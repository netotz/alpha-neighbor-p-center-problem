class PathRelinkingOrderError(Exception):
    pass


class PathRelinkingState:
    """
    Stores stateful values of a Path Relinking execution.
    """

    def __init__(self) -> None:
        self.is_running: bool = False
        """
        `True` if Path Relinking is currently running.
        Otherwise, `False`.
        """

        self.candidates_out: set[int] | None = None
        """
        Set of candidate facilities to remove from S.
        If Path Relinking, these are the open facilities in the starting solution
        but not in the target one, S_s - S_t.
        Otherwise, it is the whole set of open facilities, S.
        """

        self.candidates_in: set[int] | None = None
        """
        Set of candidate facilities to insert into S.
        If Path Relinking, these are the open facilities in the target solution
        but not in the starting one, S_t - S_s.
        Otherwise, it is the whole set of closed facilities, F - S.
        """

    def are_there_candidates(self) -> bool:
        """
        Returns whether or not there are more than 1 available candidates to be swapped.
        """
        return len(self.candidates_in) > 1

    def start(self, candidates_out: set[int], candidates_in: set[int]) -> None:
        """
        Starts running Path Relinking, initializing current candidates.
        """
        if self.__is_initialized():
            raise PathRelinkingOrderError(
                "Attempting to restart an already initialized Path Relinking state."
            )

        self.is_running = True
        self.candidates_out = candidates_out
        self.candidates_in = candidates_in

    def pause(self) -> None:
        """
        Temporarily pauses Path Relinking, keeping current candidates.
        """
        self.__raise_if_uninitialized(
            "Attempting to pause an uninitialized Path Relinking state."
        )

        if self.__is_paused():
            raise PathRelinkingOrderError(
                "Attempting to pause an already paused Path Relinking state."
            )

        self.is_running = False

    def resume(self) -> None:
        """
        Resumes Path Relinking.
        """
        self.__raise_if_uninitialized(
            "Attempting to resume an uninitialized Path Relinking state."
        )

        if not self.__is_paused():
            raise PathRelinkingOrderError(
                "Attempting to resume an already ongoing Path Relinking state."
            )

        self.is_running = True

    def end(self) -> None:
        """
        Stops and ends Path Relinking, current candidates are lost and reset to `None`.
        """
        self.__raise_if_uninitialized(
            "Attempting to end an uninitialized Path Relinking state."
        )

        self.is_running = False
        self.candidates_out = None
        self.candidates_in = None

    def update_candidates(self, inserted: int, removed: int) -> None:
        """
        Removes `inserted` from `candidates_in` and `removed` from `candidates_out`.

        Call this method after an applied swap during Path Relinking.
        """
        self.__raise_if_uninitialized(
            "Cannot update an uninitialized Path Relinking state."
        )

        self.candidates_in.remove(inserted)
        self.candidates_out.remove(removed)

    def __is_initialized(self) -> bool:
        return self.candidates_in is not None and self.candidates_out is not None

    def __raise_if_uninitialized(self, message: str) -> None:
        if not self.__is_initialized():
            raise PathRelinkingOrderError(message)

    def __is_paused(self) -> bool:
        return self.__is_initialized() and not self.is_running
