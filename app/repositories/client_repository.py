"""Read-only data access for distributed client records."""

from typing import Any

from app.core.database import DatabaseManager, database_manager
from app.core.exceptions import DatabaseConflictError, DatabaseNotFoundError, DatabaseQueryError
from app.schemas.client import ClientCreate, ClientUpdate


class ClientRepository:
    """Runs client queries against the distributed client view."""

    def __init__(self, database: DatabaseManager = database_manager) -> None:
        self._database = database

    def get_all_clients(self) -> list[dict[str, Any]]:
        """Return all clients exposed by the distributed view."""
        return self._database.fetch_all(
            """
            SELECT id_cliente, nombre, apellido, direccion, email, telefono, id_sede
            FROM dbo.vw_Cliente
            ORDER BY id_cliente;
            """
        )

    def create_client(self, client_data: ClientCreate) -> dict[str, Any]:
        """Create a client exclusively through the distributed stored procedure."""
        query = """
            EXEC dbo.usp_Cliente_Crear
                @id_cliente = ?,
                @nombre = ?,
                @apellido = ?,
                @direccion = ?,
                @email = ?,
                @telefono = ?,
                @id_sede = ?;
        """
        parameters = (
            client_data.id_cliente,
            client_data.nombre,
            client_data.apellido,
            client_data.direccion,
            client_data.email,
            client_data.telefono,
            client_data.id_sede,
        )
        try:
            result = self._database.execute_and_fetch_one(query, parameters)
        except DatabaseQueryError as error:
            if self._is_duplicate_error(error):
                raise DatabaseConflictError("El identificador de cliente ya existe.") from error
            raise

        if result is None:
            raise DatabaseQueryError("The stored procedure did not return a result.")
        if not bool(result.get("success")):
            message = str(result.get("message", "")).lower()
            if "existe" in message or "duplicate" in message:
                raise DatabaseConflictError("El identificador de cliente ya existe.")
            raise DatabaseQueryError("The stored procedure reported an unsuccessful result.")
        return result

    def update_client(
        self, id_cliente: int, id_sede: str, client_data: ClientUpdate
    ) -> dict[str, Any]:
        """Update one client exclusively through the distributed stored procedure."""
        query = """
            EXEC dbo.usp_Cliente_Actualizar
                @id_cliente = ?,
                @id_sede = ?,
                @nombre = ?,
                @apellido = ?,
                @direccion = ?,
                @email = ?,
                @telefono = ?;
        """
        result = self._database.execute_and_fetch_one(
            query,
            (
                id_cliente,
                id_sede,
                client_data.nombre,
                client_data.apellido,
                client_data.direccion,
                client_data.email,
                client_data.telefono,
            ),
        )
        if result is None:
            raise DatabaseQueryError("The stored procedure did not return a result.")
        if not bool(result.get("success")):
            message = str(result.get("message", "")).lower()
            if "no existe" in message or "no encontrado" in message:
                raise DatabaseNotFoundError("El cliente no existe en la sede indicada.")
            raise DatabaseQueryError("The stored procedure reported an unsuccessful result.")
        return result

    def delete_client(self, id_cliente: int, id_sede: str) -> dict[str, Any]:
        """Delete one client exclusively through the distributed stored procedure."""
        query = """
            EXEC dbo.usp_Cliente_Eliminar
                @id_cliente = ?,
                @id_sede = ?;
        """
        try:
            result = self._database.execute_and_fetch_one(query, (id_cliente, id_sede))
        except DatabaseQueryError as error:
            if self._is_invoice_conflict_error(error):
                raise DatabaseConflictError("El cliente tiene facturas relacionadas.") from error
            raise

        if result is None:
            raise DatabaseQueryError("The stored procedure did not return a result.")
        if not bool(result.get("success")):
            message = str(result.get("message", "")).lower()
            if "no existe" in message or "no encontrado" in message:
                raise DatabaseNotFoundError("El cliente no existe en la sede indicada.")
            if "factura" in message:
                raise DatabaseConflictError("El cliente tiene facturas relacionadas.")
            raise DatabaseQueryError("The stored procedure reported an unsuccessful result.")
        return result

    @staticmethod
    def _is_duplicate_error(error: DatabaseQueryError) -> bool:
        technical_error = str(error.__cause__ or "").lower()
        return any(marker in technical_error for marker in ("2601", "2627", "duplicate", "unique"))

    @staticmethod
    def _is_invoice_conflict_error(error: DatabaseQueryError) -> bool:
        technical_error = str(error.__cause__ or "").lower()
        return "factura" in technical_error
