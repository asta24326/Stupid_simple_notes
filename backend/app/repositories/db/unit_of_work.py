import psycopg
from backend.app.unit_of_work_interface import UnitOfWorkInterface


class DbUnitOfWork(UnitOfWorkInterface):
    """Commits or rolls back the transaction of one database connection"""

    def __init__(self, connection: psycopg.Connection) -> None:
        """Take the same open connection the repository works on (dependency injection)"""
        self._connection = connection

    def commit(self) -> None:
        """Save everything the block changed"""
        self._connection.commit()

    def rollback(self) -> None:
        """Throw away everything the block changed"""
        self._connection.rollback()
