"""Data access for distributed inventory records."""

from typing import Any

from app.core.database import DatabaseManager, database_manager
from app.core.exceptions import DatabaseConflictError, DatabaseNotFoundError, DatabaseQueryError
from app.schemas.inventory import InventoryCreate, InventoryUpdate


class InventoryRepository:
    """Uses only distributed views and inventory stored procedures."""

    def __init__(self, database: DatabaseManager = database_manager) -> None:
        self._database = database

    def get_all_inventory(self) -> list[dict[str, Any]]:
        return self._database.fetch_all(
            """
            SELECT i.id_producto, i.id_sede, i.cantidad, p.nombre AS nombre_producto
            FROM dbo.vw_Inventario AS i
            INNER JOIN dbo.vw_Producto AS p ON p.id_producto = i.id_producto
            ORDER BY i.id_producto, i.id_sede;
            """
        )

    def create_inventory(self, inventory_data: InventoryCreate) -> dict[str, Any]:
        return self._execute_inventory_procedure(
            """
            EXEC dbo.usp_Inventario_Crear
                @id_producto = ?, @id_sede = ?, @cantidad = ?;
            """,
            (inventory_data.id_producto, inventory_data.id_sede, inventory_data.cantidad),
            creating=True,
        )

    def update_inventory(
        self, id_producto: int, id_sede: str, inventory_data: InventoryUpdate
    ) -> dict[str, Any]:
        return self._execute_inventory_procedure(
            """
            EXEC dbo.usp_Inventario_Actualizar
                @id_producto = ?, @id_sede = ?, @cantidad = ?;
            """,
            (id_producto, id_sede, inventory_data.cantidad),
        )

    def delete_inventory(self, id_producto: int, id_sede: str) -> dict[str, Any]:
        return self._execute_inventory_procedure(
            """
            EXEC dbo.usp_Inventario_Eliminar
                @id_producto = ?, @id_sede = ?;
            """,
            (id_producto, id_sede),
        )

    def _execute_inventory_procedure(
        self, query: str, parameters: tuple[Any, ...], creating: bool = False
    ) -> dict[str, Any]:
        try:
            result = self._database.execute_and_fetch_one(query, parameters)
        except DatabaseQueryError as error:
            technical_error = str(error.__cause__ or "").lower()
            if creating and any(marker in technical_error for marker in ("2601", "2627", "duplicate", "unique")):
                raise DatabaseConflictError("El inventario ya existe para ese producto y sede.") from error
            if "no existe" in technical_error or "not found" in technical_error:
                raise DatabaseNotFoundError("El producto o inventario no existe.") from error
            raise
        if result is None or result.get("id_producto") is None or result.get("id_sede") is None:
            raise DatabaseQueryError("The stored procedure did not return inventory identifiers.")
        return result
