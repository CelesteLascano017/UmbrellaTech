"""Pydantic DTOs for product API requests."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _ProductFields(BaseModel):
    """Shared mutable product fields."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(min_length=1, max_length=100)
    marca: str | None = Field(default=None, max_length=50)
    modelo: str | None = Field(default=None, max_length=50)
    descripcion: str | None = Field(default=None, max_length=200)
    precio: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)

    @field_validator("marca", "modelo", "descripcion", mode="after")
    @classmethod
    def empty_optional_values_to_none(cls, value: str | None) -> str | None:
        return value or None


class ProductCreate(_ProductFields):
    """Validated payload for creating a product."""

    id_producto: int = Field(gt=0)


class ProductUpdate(_ProductFields):
    """Validated mutable fields for an existing product."""
