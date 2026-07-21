"""Pydantic DTOs for invoice API requests."""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _InvoiceFields(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    id_empleado: int = Field(gt=0)
    id_cliente: int | None = Field(default=None, gt=0)
    fecha: date | None = None
    total: Decimal = Field(ge=0, max_digits=10, decimal_places=2)


class InvoiceCreate(_InvoiceFields):
    id_factura: int = Field(gt=0)
    id_sede: Literal["001", "002"]


class InvoiceUpdate(_InvoiceFields):
    """Mutable invoice fields; its identity is carried by the URL."""
