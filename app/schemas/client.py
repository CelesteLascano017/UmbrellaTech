"""Pydantic DTOs for client API requests."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClientCreate(BaseModel):
    """Validated payload for creating a distributed client."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id_cliente: int = Field(gt=0)
    nombre: str = Field(min_length=1, max_length=50)
    apellido: str = Field(min_length=1, max_length=50)
    direccion: str | None = Field(default=None, max_length=150)
    email: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)
    id_sede: Literal["001", "002"]

    @field_validator("direccion", "email", "telefono", mode="after")
    @classmethod
    def empty_optional_values_to_none(cls, value: str | None) -> str | None:
        """Store optional blank values as SQL NULL-compatible values."""
        return value or None


class ClientUpdate(BaseModel):
    """Validated mutable fields for an existing client."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(min_length=1, max_length=50)
    apellido: str = Field(min_length=1, max_length=50)
    direccion: str | None = Field(default=None, max_length=150)
    email: str | None = Field(default=None, max_length=100)
    telefono: str | None = Field(default=None, max_length=20)

    @field_validator("direccion", "email", "telefono", mode="after")
    @classmethod
    def empty_optional_values_to_none(cls, value: str | None) -> str | None:
        """Store optional blank values as SQL NULL-compatible values."""
        return value or None
