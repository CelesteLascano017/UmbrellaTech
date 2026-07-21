"""Application service for product operations."""

from typing import Any

from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    """Coordinates product use cases without handling replication."""

    def __init__(self, repository: ProductRepository | None = None) -> None:
        self._repository = repository or ProductRepository()

    def get_all_products(self) -> list[dict[str, Any]]:
        return self._repository.get_all_products()

    def create_product(self, product_data: ProductCreate) -> dict[str, Any]:
        return self._repository.create_product(product_data)

    def update_product(self, id_producto: int, product_data: ProductUpdate) -> dict[str, Any]:
        self._validate_id(id_producto)
        return self._repository.update_product(id_producto, product_data)

    def delete_product(self, id_producto: int) -> dict[str, Any]:
        self._validate_id(id_producto)
        return self._repository.delete_product(id_producto)

    @staticmethod
    def _validate_id(id_producto: int) -> None:
        if id_producto <= 0:
            raise ValueError("Product identifier must be greater than zero.")
