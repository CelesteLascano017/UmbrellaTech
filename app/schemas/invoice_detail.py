"""Pydantic DTOs for invoice-detail requests."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class InvoiceDetailCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    id_factura: int = Field(gt=0)
    id_sede: Literal["001", "002"]
    id_producto: int = Field(gt=0)
    num_linea: int = Field(gt=0)
    cantidad: int = Field(gt=0)
    precio_unitario: Decimal = Field(ge=0, max_digits=10, decimal_places=2)


class InvoiceDetailUpdate(BaseModel):
    cantidad: int = Field(gt=0)
    precio_unitario: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
