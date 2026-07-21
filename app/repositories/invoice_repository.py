"""Data access for distributed invoice records."""

from typing import Any

from app.core.database import DatabaseManager, database_manager
from app.core.exceptions import DatabaseConflictError, DatabaseNotFoundError, DatabaseQueryError
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate


class InvoiceRepository:
    def __init__(self, database: DatabaseManager = database_manager) -> None:
        self._database = database

    def get_all_invoices(self) -> list[dict[str, Any]]:
        return self._database.fetch_all("""
            WITH Empleados AS (
                SELECT id_empleado, id_sede, nombre, apellido FROM dbo.Empleado_Admin_001
                UNION ALL
                SELECT id_empleado, id_sede, nombre, apellido FROM [DUMDUM].[TIENDA_SUR].[dbo].[Empleado_Admin_002]
            )
            SELECT f.id_factura, f.id_empleado, CONCAT(e.nombre, ' ', e.apellido) AS empleado_nombre,
                   f.id_sede, f.id_cliente,
                   CASE WHEN c.id_cliente IS NULL THEN NULL ELSE CONCAT(c.nombre, ' ', c.apellido) END AS cliente_nombre,
                   f.fecha, f.total
            FROM dbo.vw_Factura AS f
            LEFT JOIN Empleados AS e ON e.id_empleado = f.id_empleado AND e.id_sede = f.id_sede
            LEFT JOIN dbo.vw_Cliente AS c ON c.id_cliente = f.id_cliente AND c.id_sede = f.id_sede
            ORDER BY f.fecha DESC, f.id_factura, f.id_sede;
        """)

    def get_all_admin_employees(self) -> list[dict[str, Any]]:
        return self._database.fetch_all("""
            SELECT id_empleado, id_sede, nombre, apellido, CONCAT(nombre, ' ', apellido) AS nombre_completo FROM dbo.Empleado_Admin_001
            UNION ALL
            SELECT id_empleado, id_sede, nombre, apellido, CONCAT(nombre, ' ', apellido) AS nombre_completo FROM [DUMDUM].[TIENDA_SUR].[dbo].[Empleado_Admin_002]
            ORDER BY id_sede, id_empleado;
        """)

    def create_invoice(self, data: InvoiceCreate) -> dict[str, Any]:
        return self._execute("EXEC dbo.usp_Factura_Crear @id_factura = ?, @id_empleado = ?, @id_sede = ?, @id_cliente = ?, @fecha = ?, @total = ?;", (data.id_factura, data.id_empleado, data.id_sede, data.id_cliente, data.fecha, data.total), True)

    def update_invoice(self, id_factura: int, id_sede: str, data: InvoiceUpdate) -> dict[str, Any]:
        return self._execute("EXEC dbo.usp_Factura_Actualizar @id_factura = ?, @id_sede = ?, @id_empleado = ?, @id_cliente = ?, @fecha = ?, @total = ?;", (id_factura, id_sede, data.id_empleado, data.id_cliente, data.fecha, data.total))

    def delete_invoice(self, id_factura: int, id_sede: str) -> dict[str, Any]:
        return self._execute("EXEC dbo.usp_Factura_Eliminar @id_factura = ?, @id_sede = ?;", (id_factura, id_sede), False, True)

    def _execute(self, query: str, parameters: tuple[Any, ...], creating: bool = False, deleting: bool = False) -> dict[str, Any]:
        try:
            result = self._database.execute_and_fetch_one(query, parameters)
        except DatabaseQueryError as error:
            details = str(error.__cause__ or "").lower()
            if creating and any(marker in details for marker in ("2601", "2627", "duplicate", "unique")):
                raise DatabaseConflictError("La factura ya existe en la sede.") from error
            if deleting and "detalle" in details:
                raise DatabaseConflictError("La factura tiene detalles relacionados.") from error
            if "no existe" in details or "not found" in details:
                raise DatabaseNotFoundError("La factura, cliente o empleado no existe.") from error
            raise
        if result is None or result.get("id_factura") is None or result.get("id_sede") is None:
            raise DatabaseQueryError("The stored procedure did not return invoice identifiers.")
        return result
