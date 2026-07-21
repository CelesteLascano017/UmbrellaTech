"""Safe application exceptions for database infrastructure."""


class DatabaseError(Exception):
    """Base exception for database infrastructure errors."""


class DatabaseConnectionError(DatabaseError):
    """Raised when SQL Server cannot be reached."""


class DatabaseQueryError(DatabaseError):
    """Raised when a SQL query cannot be executed."""


class DatabaseConflictError(DatabaseError):
    """Raised when an operation conflicts with existing database data."""


class DatabaseNotFoundError(DatabaseError):
    """Raised when a database operation cannot find its target."""


class DatabaseTransactionError(DatabaseError):
    """Raised when a transaction cannot be completed."""
