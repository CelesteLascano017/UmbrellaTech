"""Generic, short-lived SQL Server access infrastructure."""

import logging
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Any

import pyodbc

from app.core.config import Settings, get_settings
from app.core.exceptions import (
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseTransactionError,
)

logger = logging.getLogger(__name__)


def _odbc_value(value: str) -> str:
    """Return a safely braced ODBC connection-string value."""
    return "{" + value.replace("}", "}}") + "}"


def _odbc_error_details(error: pyodbc.Error) -> tuple[str, str]:
    """Extract technical ODBC codes without logging the connection string."""
    sqlstate = str(error.args[0]) if error.args else "unknown"
    native_code = "unknown"
    if len(error.args) > 1:
        message = str(error.args[1])
        for token in reversed(message.replace("(", " ").replace(")", " ").split()):
            if token.lstrip("-").isdigit():
                native_code = token
                break
    return sqlstate, native_code


class DatabaseManager:
    """Executes parameterized queries with connections scoped to each operation."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        pyodbc.pooling = True

    def _connection_string(self) -> str:
        settings = self._settings
        return (
            f"DRIVER={{{settings.db_driver}}};"
            f"SERVER={_odbc_value(settings.db_server)};"
            f"DATABASE={_odbc_value(settings.db_database)};"
            f"UID={_odbc_value(settings.db_user)};"
            f"PWD={_odbc_value(settings.db_password)};"
            f"Encrypt={'yes' if settings.db_encrypt else 'no'};"
            "TrustServerCertificate="
            f"{'yes' if settings.db_trust_server_certificate else 'no'};"
            f"Connection Timeout={settings.db_connection_timeout};"
        )

    @contextmanager
    def connection(self) -> Iterator[pyodbc.Connection]:
        """Open a pooled connection only for the duration of the context."""
        connection: pyodbc.Connection | None = None
        try:
            connection = pyodbc.connect(self._connection_string(), autocommit=False)
            yield connection
        except pyodbc.Error as error:
            sqlstate, native_code = _odbc_error_details(error)
            logger.exception(
                "SQL Server connection failed (sqlstate=%s, native_code=%s): %s",
                sqlstate,
                native_code,
                error,
            )
            raise DatabaseConnectionError("No fue posible conectar con SQL Server.") from error
        finally:
            if connection is not None:
                connection.close()

    @contextmanager
    def _cursor(self, connection: pyodbc.Connection) -> Iterator[pyodbc.Cursor]:
        try:
            with connection.cursor() as cursor:
                yield cursor
        except pyodbc.Error as error:
            sqlstate, native_code = _odbc_error_details(error)
            logger.exception(
                "SQL query failed (sqlstate=%s, native_code=%s): %s",
                sqlstate,
                native_code,
                error,
            )
            raise DatabaseQueryError("No fue posible ejecutar la consulta de base de datos.") from error

    @staticmethod
    def _rows_to_dicts(cursor: pyodbc.Cursor, rows: Sequence[pyodbc.Row]) -> list[dict[str, Any]]:
        columns = [column[0] for column in cursor.description or []]
        return [dict(zip(columns, row)) for row in rows]

    def fetch_all(self, query: str, parameters: Sequence[Any] = ()) -> list[dict[str, Any]]:
        """Execute a parameterized SELECT query and return all rows."""
        with self.connection() as connection, self._cursor(connection) as cursor:
            cursor.execute(query, tuple(parameters))
            return self._rows_to_dicts(cursor, cursor.fetchall())

    def fetch_one(self, query: str, parameters: Sequence[Any] = ()) -> dict[str, Any] | None:
        """Execute a parameterized SELECT query and return the first row, if any."""
        with self.connection() as connection, self._cursor(connection) as cursor:
            cursor.execute(query, tuple(parameters))
            row = cursor.fetchone()
            if row is None:
                return None
            return self._rows_to_dicts(cursor, [row])[0]

    def execute_and_fetch_one(
        self, query: str, parameters: Sequence[Any] = ()
    ) -> dict[str, Any] | None:
        """Execute a parameterized command and return its first result row."""
        with self.connection() as connection:
            try:
                with self._cursor(connection) as cursor:
                    cursor.execute(query, tuple(parameters))
                    while cursor.description is None:
                        if not cursor.nextset():
                            connection.commit()
                            return None
                    row = cursor.fetchone()
                    result = None if row is None else self._rows_to_dicts(cursor, [row])[0]
                connection.commit()
                return result
            except DatabaseQueryError:
                connection.rollback()
                logger.warning("SQL operation rolled back.")
                raise

    def execute(self, query: str, parameters: Sequence[Any] = ()) -> int:
        """Execute a parameterized write query and commit it."""
        with self.connection() as connection:
            try:
                with self._cursor(connection) as cursor:
                    cursor.execute(query, tuple(parameters))
                    affected_rows = cursor.rowcount
                connection.commit()
                return affected_rows
            except DatabaseQueryError:
                connection.rollback()
                logger.warning("SQL operation rolled back.")
                raise

    def execute_transaction(self, statements: Sequence[tuple[str, Sequence[Any]]]) -> list[int]:
        """Execute statements atomically on one SQL Server connection."""
        connection: pyodbc.Connection | None = None
        try:
            with self.connection() as connection:
                affected_rows: list[int] = []
                with self._cursor(connection) as cursor:
                    for query, parameters in statements:
                        cursor.execute(query, tuple(parameters))
                        affected_rows.append(cursor.rowcount)
                connection.commit()
                return affected_rows
        except (DatabaseConnectionError, DatabaseQueryError) as error:
            if connection is not None:
                connection.rollback()
            logger.error("Transaction rolled back.")
            raise DatabaseTransactionError("No fue posible completar la transacción.") from error


database_manager = DatabaseManager()
