"""HTTP API for invoice operations."""

from typing import Any, Literal

from fastapi import APIRouter, Path, status
from fastapi.responses import JSONResponse

from app.core.exceptions import DatabaseConflictError, DatabaseError, DatabaseNotFoundError
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])
invoice_service = InvoiceService()


def _error(code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=code, content={"success": False, "message": message, "errors": {}})


@router.get("")
def get_all_invoices() -> dict[str, Any]:
    try: return {"success": True, "message": "Facturas obtenidas correctamente.", "data": invoice_service.get_all_invoices()}
    except DatabaseError: return _error(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible obtener las facturas.")


@router.get("/employees")
def get_all_admin_employees() -> dict[str, Any]:
    try: return {"success": True, "message": "Empleados obtenidos correctamente.", "data": invoice_service.get_all_admin_employees()}
    except DatabaseError: return _error(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible obtener los empleados.")


@router.post("", status_code=status.HTTP_201_CREATED)
def create_invoice(data: InvoiceCreate) -> dict[str, Any]:
    try:
        result = invoice_service.create_invoice(data)
        return {"success": True, "message": "Factura registrada correctamente.", "data": {"id_factura": result["id_factura"], "id_sede": result["id_sede"]}}
    except DatabaseConflictError: return _error(status.HTTP_409_CONFLICT, "La factura ya existe en la sede.")
    except DatabaseNotFoundError: return _error(status.HTTP_404_NOT_FOUND, "El empleado o cliente no existe en la sede.")
    except DatabaseError: return _error(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible registrar la factura.")


@router.put("/{id_factura}/{id_sede}")
def update_invoice(data: InvoiceUpdate, id_factura: int = Path(gt=0), id_sede: Literal["001", "002"] = Path()) -> dict[str, Any]:
    try:
        result = invoice_service.update_invoice(id_factura, id_sede, data)
        return {"success": True, "message": "Factura actualizada correctamente.", "data": {"id_factura": result["id_factura"], "id_sede": result["id_sede"]}}
    except DatabaseNotFoundError: return _error(status.HTTP_404_NOT_FOUND, "La factura, empleado o cliente no existe.")
    except DatabaseError: return _error(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible actualizar la factura.")


@router.delete("/{id_factura}/{id_sede}")
def delete_invoice(id_factura: int = Path(gt=0), id_sede: Literal["001", "002"] = Path()) -> dict[str, Any]:
    try:
        result = invoice_service.delete_invoice(id_factura, id_sede)
        return {"success": True, "message": "Factura eliminada correctamente.", "data": {"id_factura": result["id_factura"], "id_sede": result["id_sede"]}}
    except DatabaseConflictError: return _error(status.HTTP_409_CONFLICT, "No se puede eliminar la factura porque tiene detalles.")
    except DatabaseNotFoundError: return _error(status.HTTP_404_NOT_FOUND, "La factura no existe.")
    except DatabaseError: return _error(status.HTTP_503_SERVICE_UNAVAILABLE, "No fue posible eliminar la factura.")
