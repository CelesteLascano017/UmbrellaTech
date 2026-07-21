"""Pydantic DTOs for inventory API requests."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class InventoryCreate(BaseModel):
    """Validated payload for creating inventory."""

    model_config = ConfigDict(str_strip_whitespace=True)

    id_producto: int = Field(gt=0)
    id_sede: Literal["001", "002"]
    cantidad: int = Field(ge=0)


class InventoryUpdate(BaseModel):
    """Validated mutable field for an inventory record."""

    cantidad: int = Field(ge=0)
