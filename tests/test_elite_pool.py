import pytest

from anpcp.models.elite_pool import ElitePool
from anpcp.models.solution import Solution
from anpcp.models.solution_set import SolutionSet


@pytest.mark.parametrize("limit", [0, -1])
def test_init_invalidLimits_raisesValueError(limit: int):
    with pytest.raises(ValueError):
        ElitePool(limit)


@pytest.mark.parametrize("limit", [1, 20])
def test_init_validLimits_returnsInstance(limit: int):
    pool = ElitePool(limit)
    assert isinstance(pool, ElitePool)


@pytest.mark.parametrize("limit", [1, 2])
def test_len_fullPool_equalsLimit(limit: int):
    pool = ElitePool(limit)

    for _ in range(limit):
        pool.try_add(SolutionSet(1))

    assert len(pool) == limit


def test_tryAdd_underLimit_returnsTrue():
    pool = ElitePool(1)

    assert pool.try_add(SolutionSet(1))


def test_tryAdd_underLimitAndBetterThanBest_returnsTrueAndUpdatesBest():
    pool = ElitePool(2)

    best = SolutionSet(2)
    pool.try_add(best)

    better = SolutionSet(1)
    assert pool.try_add(better)
    assert pool.get_best() == better


@pytest.mark.parametrize(
    ("limit", "solutions", "better", "new_worst_obj_func"),
    [
        [
            1,
            [SolutionSet(2)],
            SolutionSet(1),
            1,
        ],
        # added is new worst
        [
            2,
            [SolutionSet(3), SolutionSet(1)],
            SolutionSet(2),
            2,
        ],
        # solution already in pool is new worst
        [
            2,
            [SolutionSet(3), SolutionSet(2)],
            SolutionSet(1),
            2,
        ],
    ],
)
def test_tryAdd_overLimitAndBetterThanWorst_returnsTrueAndUpdatesWorst(
    limit: int,
    solutions: list[SolutionSet],
    better: SolutionSet,
    new_worst_obj_func: int,
):
    pool = ElitePool(limit)

    # reach limit
    for solution in solutions:
        pool.try_add(solution)

    assert pool.try_add(better)
    assert pool.get_worst().obj_func == new_worst_obj_func


def test_tryAdd_overLimitAndBetterThanBest_returnsTrueAndUpdatesBest():
    pool = ElitePool(1)

    best = SolutionSet(2)
    # limit reached
    pool.try_add(best)

    better = SolutionSet(1)
    assert pool.try_add(better)
    assert pool.get_best() == better


def test_tryAdd_overLimitAndWorseThanWorst_returnsFalseAndKeepsWorst():
    pool = ElitePool(1)

    worst = SolutionSet(1)
    # limit reached
    pool.try_add(worst)

    worse = SolutionSet(2)
    assert not pool.try_add(worse)
    assert pool.get_worst() == worst
