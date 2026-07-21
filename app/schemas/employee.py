"""Pydantic DTOs for employee requests."""
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,field_validator
class _EmployeeFields(BaseModel):
 model_config=ConfigDict(str_strip_whitespace=True)
 nombre:str=Field(min_length=1,max_length=50); apellido:str=Field(min_length=1,max_length=50)
 NIC:str|None=Field(default=None,max_length=20); edad:int|None=Field(default=None,ge=0)
 telefono:str|None=Field(default=None,max_length=20); sueldo:Decimal|None=Field(default=None,ge=0,max_digits=10,decimal_places=2)
 @field_validator("NIC","telefono",mode="after")
 @classmethod
 def empty_to_none(cls,v:str|None)->str|None:return v or None
class EmployeeCreate(_EmployeeFields):
 id_empleado:int=Field(gt=0); id_sede:Literal["001","002"]
class EmployeeUpdate(_EmployeeFields): pass
