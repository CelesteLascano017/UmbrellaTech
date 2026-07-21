"""HTTP API for product operations."""

import logging

from typing import Any

from fastapi import APIRouter, Path, status
from fastapi.responses import JSONResponse

from app.core.exceptions import DatabaseConflictError, DatabaseError, DatabaseNotFoundError
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["Products"])
product_service = ProductService()
logger = logging.getLogger(__name__)


def _error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"success": False, "message": message, "errors": {}})


@router.get("")
def get_all_products() -> dict[str, Any]:
    try:
        return {"success": True, "message": "Productos obtenidos correctamente.", "data": product_service.get_all_products()}
    except DatabaseError:
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible obtener los productos.")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate) -> dict[str, Any]:
    try:
        result = product_service.create_product(product_data)
        return {"success": True, "message": "Producto creado correctamente.", "data": {"id_producto": result["id_producto"]}}
    except DatabaseConflictError:
        return _error_response(status.HTTP_409_CONFLICT, "El identificador de producto ya existe.")
    except DatabaseError as error:
        logger.exception("Product creation failed in API router: %s", error)
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible crear el producto.")


@router.put("/{id_producto}")
def update_product(product_data: ProductUpdate, id_producto: int = Path(gt=0)) -> dict[str, Any]:
    try:
        result = product_service.update_product(id_producto, product_data)
        return {"success": True, "message": "Producto actualizado correctamente.", "data": {"id_producto": result["id_producto"]}}
    except DatabaseNotFoundError:
        return _error_response(status.HTTP_404_NOT_FOUND, "El producto no existe.")
    except DatabaseError:
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible actualizar el producto.")


@router.delete("/{id_producto}")
def delete_product(id_producto: int = Path(gt=0)) -> dict[str, Any]:
    try:
        result = product_service.delete_product(id_producto)
        return {"success": True, "message": "Producto eliminado correctamente.", "data": {"id_producto": result["id_producto"]}}
    except DatabaseNotFoundError:
        return _error_response(status.HTTP_404_NOT_FOUND, "El producto no existe.")
    except DatabaseConflictError:
        return _error_response(status.HTTP_409_CONFLICT, "No se puede eliminar el producto porque tiene facturas relacionadas.")
    except DatabaseError:
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible eliminar el producto.")
