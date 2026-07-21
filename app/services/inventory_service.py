"""Application service for inventory operations."""

from typing import Any

from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import InventoryCreate, InventoryUpdate


class InventoryService:
    """Coordinates inventory use cases without fragment routing."""

    def __init__(self, repository: InventoryRepository | None = None) -> None:
        self._repository = repository or InventoryRepository()

    def get_all_inventory(self) -> list[dict[str, Any]]:
        return self._repository.get_all_inventory()

    def create_inventory(self, inventory_data: InventoryCreate) -> dict[str, Any]:
        self._validate_identity(inventory_data.id_producto, inventory_data.id_sede)
        if inventory_data.cantidad < 0:
            raise ValueError("Quantity must not be negative.")
        return self._repository.create_inventory(inventory_data)

    def update_inventory(self, id_producto: int, id_sede: str, inventory_data: InventoryUpdate) -> dict[str, Any]:
        self._validate_identity(id_producto, id_sede)
        if inventory_data.cantidad < 0:
            raise ValueError("Quantity must not be negative.")
        return self._repository.update_inventory(id_producto, id_sede, inventory_data)

    def delete_inventory(self, id_producto: int, id_sede: str) -> dict[str, Any]:
        self._validate_identity(id_producto, id_sede)
        return self._repository.delete_inventory(id_producto, id_sede)

    @staticmethod
    def _validate_identity(id_producto: int, id_sede: str) -> None:
        if id_producto <= 0:
            raise ValueError("Product identifier must be greater than zero.")
        if id_sede not in {"001", "002"}:
            raise ValueError("Invalid branch identifier.")
