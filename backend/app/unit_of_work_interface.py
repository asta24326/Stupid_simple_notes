from abc import ABC, abstractmethod
from types import TracebackType


class UnitOfWorkInterface(ABC):
    """Boundary of one buisness transaction: everuthing inside the 'with' block is 'saved' together or not at all."""

    def __enter__(self) -> "UnitOfWorkInterface":
        """Start of the block: the transaction begins with the first query, so there is nothing to prepare"""
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        """End of the block, commit if it finished normally, roolback if an exeption came out of it"""

        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    @abstractmethod
    def commit(self) -> None:
        """Make all changes of the block permanent"""

    @abstractmethod
    def rollback(self) -> None:
        """Throw all changes of the block away."""
