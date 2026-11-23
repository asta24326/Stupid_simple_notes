import pytest

from tests.fakes import FakeUnitOfWork


def test_commits_when_the_block_finishes():
    """A block without an exception ends with exactly one commit"""

    unit_of_work = FakeUnitOfWork()

    with unit_of_work:
        pass

    assert unit_of_work.commits == 1
    assert unit_of_work.rollbacks == 0


def test_rolls_back_when_block_raises():
    """An exception inside the block ends with a rollback and no commit"""
    unit_of_work = FakeUnitOfWork()

    with pytest.raises(RuntimeError):
        with unit_of_work:
            raise RuntimeError("failure inside the block")

    assert unit_of_work.commits == 0
    assert unit_of_work.rollbacks == 1
