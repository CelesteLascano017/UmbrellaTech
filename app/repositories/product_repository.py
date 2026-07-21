"""Data access for replicated product records."""

from typing import Any

from app.core.database import DatabaseManager, database_manager
from app.core.exceptions import DatabaseConflictError, DatabaseNotFoundError, DatabaseQueryError
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    """Runs product queries only against the published node database."""

    def __init__(self, database: DatabaseManager = database_manager) -> None:
        self._database = database

    def get_all_products(self) -> list[dict[str, Any]]:
        return self._database.fetch_all(
            """
            SELECT id_producto, nombre, marca, modelo, descripcion, precio
            FROM dbo.vw_Producto
            ORDER BY id_producto;
            """
        )

    def create_product(self, product_data: ProductCreate) -> dict[str, Any]:
        result = self._run_procedure(
            """
            EXEC dbo.usp_Producto_Crear
                @id_producto = ?, @nombre = ?, @marca = ?, @modelo = ?,
                @descripcion = ?, @precio = ?;
            """,
            (product_data.id_producto, product_data.nombre, product_data.marca, product_data.modelo, product_data.descripcion, product_data.precio),
        )
        if result.get("id_producto") is None:
            raise DatabaseQueryError("The stored procedure did not return a product identifier.")
        return result

    def update_product(self, id_producto: int, product_data: ProductUpdate) -> dict[str, Any]:
        result = self._run_procedure(
            """
            EXEC dbo.usp_Producto_Actualizar
                @id_producto = ?, @nombre = ?, @marca = ?, @modelo = ?,
                @descripcion = ?, @precio = ?;
            """,
            (id_producto, product_data.nombre, product_data.marca, product_data.modelo, product_data.descripcion, product_data.precio),
        )
        if result.get("id_producto") is None:
            raise DatabaseQueryError("The stored procedure did not return a product identifier.")
        return result

    def delete_product(self, id_producto: int) -> dict[str, Any]:
        result = self._run_procedure(
            "EXEC dbo.usp_Producto_Eliminar @id_producto = ?;",
            (id_producto,),
        )
        if result.get("id_producto") is None:
            raise DatabaseQueryError("The stored procedure did not return a product identifier.")
        return result

    def _run_procedure(self, query: str, parameters: tuple[Any, ...]) -> dict[str, Any]:
        try:
            result = self._database.execute_and_fetch_one(query, parameters)
        except DatabaseQueryError as error:
            technical_error = str(error.__cause__ or "").lower()
            if any(code in technical_error for code in ("2601", "2627", "duplicate", "unique")):
                raise DatabaseConflictError("El identificador de producto ya existe.") from error
            if "factura" in technical_error:
                raise DatabaseConflictError("El producto tiene facturas relacionadas.") from error
            raise
        if result is None:
            raise DatabaseQueryError("The stored procedure did not return a result.")
        return result
