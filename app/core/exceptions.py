"""Safe application exceptions for database infrastructure."""


class DatabaseError(Exception):
    """Base exception for database infrastructure errors."""


class DatabaseConnectionError(DatabaseError):
    """Raised when SQL Server cannot be reached."""


class DatabaseQueryError(DatabaseError):
    """Raised when a SQL query cannot be executed."""


class DatabaseTransactionError(DatabaseError):
    """Raised when a transaction cannot be completed."""

