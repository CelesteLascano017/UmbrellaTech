"""Application service for invoice operations."""

from typing import Any

from app.repositories.invoice_repository import InvoiceRepository
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate


class InvoiceService:
    def __init__(self, repository: InvoiceRepository | None = None) -> None: self._repository = repository or InvoiceRepository()
    def get_all_invoices(self) -> list[dict[str, Any]]: return self._repository.get_all_invoices()
    def get_all_admin_employees(self) -> list[dict[str, Any]]: return self._repository.get_all_admin_employees()
    def create_invoice(self, data: InvoiceCreate) -> dict[str, Any]: self._validate(data.id_factura, data.id_sede, data.id_empleado, data.total); return self._repository.create_invoice(data)
    def update_invoice(self, id_factura: int, id_sede: str, data: InvoiceUpdate) -> dict[str, Any]: self._validate(id_factura, id_sede, data.id_empleado, data.total); return self._repository.update_invoice(id_factura, id_sede, data)
    def delete_invoice(self, id_factura: int, id_sede: str) -> dict[str, Any]: self._validate(id_factura, id_sede); return self._repository.delete_invoice(id_factura, id_sede)
    @staticmethod
    def _validate(id_factura: int, id_sede: str, id_empleado: int | None = None, total: Any = None) -> None:
        if id_factura <= 0 or id_sede not in {"001", "002"}: raise ValueError("Invalid invoice identity.")
        if id_empleado is not None and id_empleado <= 0: raise ValueError("Invalid employee identifier.")
        if total is not None and total < 0: raise ValueError("Invalid total.")
