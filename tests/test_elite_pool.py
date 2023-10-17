"""
These tests are currently out of date and won't pass.
"""

import pytest

from anpcp.models.elite_pool import ElitePool
from anpcp.models.solution import Solution
from anpcp.models.solution_set import SolutionSet


@pytest.mark.parametrize("limit", [0, -1])
def test_init_invalidLimit_raisesValueError(limit: int):
    with pytest.raises(ValueError):
        ElitePool(limit)


@pytest.mark.parametrize("min_sym_diff", [-1, -2])
def test_init_invalidMinSymmetricDiff_raisesValueError(min_sym_diff: int):
    with pytest.raises(ValueError):
        ElitePool(1, min_sym_diff)


@pytest.mark.parametrize(
    ("limit", "min_sym_diff"),
    [
        [1, 1],
        [2, 4],
    ],
)
def test_init_validArgs_returnsInstance(limit: int, min_sym_diff: int):
    mock_pool = ElitePool(limit, min_sym_diff)

    assert isinstance(mock_pool, ElitePool)


@pytest.mark.parametrize("limit", [1, 2])
def test_len_fullPool_equalsLimit(limit: int):
    mock_pool = ElitePool(limit)

    for _ in range(limit):
        stub_solution = SolutionSet(1)

        mock_pool.try_add(stub_solution)

    assert mock_pool.is_full()


def test_tryAdd_underLimit_returnsTrue():
    mock_pool = ElitePool(1)

    stub_solution = SolutionSet(1)

    assert mock_pool.try_add(stub_solution)


def test_tryAdd_underLimitAndBetterThanBest_returnsTrueAndUpdatesBest():
    mock_pool = ElitePool(2)

    stub_best_solution = SolutionSet(2)
    mock_pool.try_add(stub_best_solution)

    stub_better_solution = SolutionSet(1)

    assert mock_pool.try_add(stub_better_solution)
    assert mock_pool.get_best() == stub_better_solution


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
