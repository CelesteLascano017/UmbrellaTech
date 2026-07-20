"""Database health checks kept outside the HTTP layer."""

import logging

from app.core.database import DatabaseManager, database_manager
from app.core.exceptions import DatabaseConnectionError, DatabaseQueryError

logger = logging.getLogger(__name__)

_DISTRIBUTED_VIEWS = (
    "vw_Cliente",
    "vw_Producto",
    "vw_Inventario",
    "vw_Factura",
    "vw_Detalle_Factura",
)


class DatabaseHealthChecker:
    """Runs safe, minimal database availability checks."""

    def __init__(self, database: DatabaseManager = database_manager) -> None:
        self._database = database

    def database_identity(self) -> dict[str, object]:
        return self._database.fetch_one(
            "SELECT DB_NAME() AS database_name, @@SERVERNAME AS server_name;"
        ) or {}

    def distributed_views(self) -> dict[str, bool]:
        view_status: dict[str, bool] = {}
        for view_name in _DISTRIBUTED_VIEWS:
            try:
                self._database.fetch_one(f"SELECT TOP (1) * FROM dbo.{view_name};")
                view_status[view_name] = True
            except (DatabaseQueryError, DatabaseConnectionError):
                logger.error("Distributed view check failed for %s.", view_name)
                view_status[view_name] = False
        return view_status

    def linked_server(self) -> None:
        try:
            self._database.fetch_one("SELECT TOP (1) name FROM [DUMDUM].master.sys.databases;")
        except DatabaseQueryError:
            logger.error("Linked Server DUMDUM is unavailable.")
            raise


database_health_checker = DatabaseHealthChecker()
