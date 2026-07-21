"""Application service for client read operations."""

from typing import Any

from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate, ClientUpdate


class ClientService:
    """Coordinates client read use cases."""

    def __init__(self, repository: ClientRepository | None = None) -> None:
        self._repository = repository or ClientRepository()

    def get_all_clients(self) -> list[dict[str, Any]]:
        """Get all clients from the distributed repository."""
        return self._repository.get_all_clients()

    def create_client(self, client_data: ClientCreate) -> dict[str, Any]:
        """Create a validated client through the repository."""
        return self._repository.create_client(client_data)

    def update_client(
        self, id_cliente: int, id_sede: str, client_data: ClientUpdate
    ) -> dict[str, Any]:
        """Update a validated client without deciding its physical fragment."""
        if id_cliente <= 0:
            raise ValueError("Client identifier must be greater than zero.")
        if id_sede not in {"001", "002"}:
            raise ValueError("Invalid branch identifier.")
        return self._repository.update_client(id_cliente, id_sede, client_data)

    def delete_client(self, id_cliente: int, id_sede: str) -> dict[str, Any]:
        """Delete a client without deciding its physical fragment."""
        if id_cliente <= 0:
            raise ValueError("Client identifier must be greater than zero.")
        if id_sede not in {"001", "002"}:
            raise ValueError("Invalid branch identifier.")
        return self._repository.delete_client(id_cliente, id_sede)
