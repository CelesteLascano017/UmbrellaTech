"""HTTP API for inventory operations."""

from typing import Any, Literal

from fastapi import APIRouter, Path, status
from fastapi.responses import JSONResponse

from app.core.exceptions import DatabaseConflictError, DatabaseError, DatabaseNotFoundError
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])
inventory_service = InventoryService()


def _error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"success": False, "message": message, "errors": {}})


@router.get("")
def get_all_inventory() -> dict[str, Any]:
    try:
        return {"success": True, "message": "Inventario obtenido correctamente.", "data": inventory_service.get_all_inventory()}
    except DatabaseError:
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible obtener el inventario.")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_inventory(inventory_data: InventoryCreate) -> dict[str, Any]:
    try:
        result = inventory_service.create_inventory(inventory_data)
        return {"success": True, "message": "Inventario registrado correctamente.", "data": {"id_producto": result["id_producto"], "id_sede": result["id_sede"]}}
    except DatabaseConflictError:
        return _error_response(status.HTTP_409_CONFLICT, "El inventario ya existe para ese producto y sede.")
    except DatabaseNotFoundError:
        return _error_response(status.HTTP_404_NOT_FOUND, "El producto no existe.")
    except DatabaseError:
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible registrar el inventario.")


@router.put("/{id_producto}/{id_sede}")
def update_inventory(inventory_data: InventoryUpdate, id_producto: int = Path(gt=0), id_sede: Literal["001", "002"] = Path()) -> dict[str, Any]:
    try:
        result = inventory_service.update_inventory(id_producto, id_sede, inventory_data)
        return {"success": True, "message": "Inventario actualizado correctamente.", "data": {"id_producto": result["id_producto"], "id_sede": result["id_sede"]}}
    except DatabaseNotFoundError:
        return _error_response(status.HTTP_404_NOT_FOUND, "El registro de inventario no existe.")
    except DatabaseError:
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible actualizar el inventario.")


@router.delete("/{id_producto}/{id_sede}")
def delete_inventory(id_producto: int = Path(gt=0), id_sede: Literal["001", "002"] = Path()) -> dict[str, Any]:
    try:
        result = inventory_service.delete_inventory(id_producto, id_sede)
        return {"success": True, "message": "Inventario eliminado correctamente.", "data": {"id_producto": result["id_producto"], "id_sede": result["id_sede"]}}
    except DatabaseNotFoundError:
        return _error_response(status.HTTP_404_NOT_FOUND, "El registro de inventario no existe.")
    except DatabaseError:
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible eliminar el inventario.")
