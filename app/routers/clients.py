"""HTTP API for client operations."""

from typing import Any, Literal

from fastapi import APIRouter, Path, status
from fastapi.responses import JSONResponse

from app.core.exceptions import DatabaseConflictError, DatabaseError, DatabaseNotFoundError
from app.schemas.client import ClientCreate, ClientUpdate
from app.services.client_service import ClientService

router = APIRouter(prefix="/api/clients", tags=["Clients"])
client_service = ClientService()


def _error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "errors": {}},
    )


@router.get("")
def get_all_clients() -> dict[str, Any]:
    try:
        return {"success": True, "message": "Clientes obtenidos correctamente", "data": client_service.get_all_clients()}
    except DatabaseError:
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible obtener los clientes.")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_client(client_data: ClientCreate) -> dict[str, Any]:
    try:
        result = client_service.create_client(client_data)
        return {"success": True, "message": "Cliente registrado correctamente.", "data": {"id_cliente": result["id_cliente"], "id_sede": result["id_sede"]}}
    except DatabaseConflictError:
        return _error_response(status.HTTP_409_CONFLICT, "El identificador de cliente ya existe.")
    except DatabaseError:
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible registrar el cliente.")


@router.put("/{id_cliente}/{id_sede}")
def update_client(client_data: ClientUpdate, id_cliente: int = Path(gt=0), id_sede: Literal["001", "002"] = Path()) -> dict[str, Any]:
    try:
        result = client_service.update_client(id_cliente, id_sede, client_data)
        return {"success": True, "message": "Cliente actualizado correctamente.", "data": {"id_cliente": result["id_cliente"], "id_sede": result["id_sede"]}}
    except DatabaseNotFoundError:
        return _error_response(status.HTTP_404_NOT_FOUND, "El cliente no existe en la sede indicada.")
    except DatabaseError:
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible actualizar el cliente.")


@router.delete("/{id_cliente}/{id_sede}")
def delete_client(id_cliente: int = Path(gt=0), id_sede: Literal["001", "002"] = Path()) -> dict[str, Any]:
    """Delete a client through the distributed stored procedure."""
    try:
        result = client_service.delete_client(id_cliente, id_sede)
        return {"success": True, "message": "Cliente eliminado correctamente.", "data": {"id_cliente": result["id_cliente"], "id_sede": result["id_sede"]}}
    except DatabaseNotFoundError:
        return _error_response(status.HTTP_404_NOT_FOUND, "El cliente no existe en la sede indicada.")
    except DatabaseConflictError:
        return _error_response(status.HTTP_409_CONFLICT, "No se puede eliminar el cliente porque tiene facturas relacionadas.")
    except DatabaseError:
        return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible eliminar el cliente.")
