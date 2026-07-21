"""Data access for reconstructed employee records."""
from typing import Any
from app.core.database import DatabaseManager,database_manager
from app.core.exceptions import DatabaseConflictError,DatabaseNotFoundError,DatabaseQueryError
from app.schemas.employee import EmployeeCreate,EmployeeUpdate
class EmployeeRepository:
 def __init__(self,database:DatabaseManager=database_manager)->None:self._database=database
 def get_all_employees(self)->list[dict[str,Any]]:return self._database.fetch_all("SELECT id_empleado,id_sede,nombre,apellido,NIC,edad,telefono,sueldo FROM dbo.vw_Empleado ORDER BY id_sede,id_empleado;")
 def create_employee(self,d:EmployeeCreate)->dict[str,Any]:return self._exec("EXEC dbo.usp_Empleado_Crear @id_empleado=?,@id_sede=?,@nombre=?,@apellido=?,@NIC=?,@edad=?,@telefono=?,@sueldo=?;",(d.id_empleado,d.id_sede,d.nombre,d.apellido,d.NIC,d.edad,d.telefono,d.sueldo),True)
 def update_employee(self,i:int,s:str,d:EmployeeUpdate)->dict[str,Any]:return self._exec("EXEC dbo.usp_Empleado_Actualizar @id_empleado=?,@id_sede=?,@nombre=?,@apellido=?,@NIC=?,@edad=?,@telefono=?,@sueldo=?;",(i,s,d.nombre,d.apellido,d.NIC,d.edad,d.telefono,d.sueldo))
 def delete_employee(self,i:int,s:str)->dict[str,Any]:return self._exec("EXEC dbo.usp_Empleado_Eliminar @id_empleado=?,@id_sede=?;",(i,s))
 def _exec(self,q:str,p:tuple[Any,...],create:bool=False)->dict[str,Any]:
  try:r=self._database.execute_and_fetch_one(q,p)
  except DatabaseQueryError as e:
   t=str(e.__cause__ or "").lower()
   if create and any(x in t for x in ("2601","2627","duplicate","unique","nic")):raise DatabaseConflictError("El ID o NIC ya existe.") from e
   if "factura" in t:raise DatabaseConflictError("El empleado tiene facturas relacionadas.") from e
   if "no existe" in t or "not found" in t:raise DatabaseNotFoundError("El empleado no existe.") from e
   raise
  if r is None or r.get("id_empleado") is None or r.get("id_sede") is None:raise DatabaseQueryError("The stored procedure did not return employee identifiers.")
  return r
