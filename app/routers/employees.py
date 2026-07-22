"""HTTP API for employee operations."""
from typing import Any,Literal
from fastapi import APIRouter,Path,status
from fastapi.responses import JSONResponse
from app.core.exceptions import DatabaseConflictError,DatabaseError,DatabaseNotFoundError
from app.schemas.employee import EmployeeCreate,EmployeeUpdate
from app.services.employee_service import EmployeeService
router=APIRouter(prefix="/api/employees",tags=["Employees"]); employee_service=EmployeeService()
def err(c:int,m:str)->JSONResponse:return JSONResponse(status_code=c,content={"success":False,"message":m,"errors":{}})
def data(r:dict[str,Any])->dict[str,Any]:return {"id_empleado":r["id_empleado"],"id_sede":r["id_sede"]}
@router.get("")
def get_all_employees()->dict[str,Any]:
 try:return {"success":True,"message":"Empleados obtenidos correctamente.","data":employee_service.get_all_employees()}
 except DatabaseError:return err(503,"No fue posible obtener los empleados.")
@router.get("/fragments/{id_sede}")
def get_employee_fragments(id_sede:Literal["001","002"]=Path())->dict[str,Any]:
 try:return {"success":True,"message":"Fragmentos de empleados obtenidos correctamente.","data":employee_service.get_employee_fragments(id_sede)}
 except DatabaseError:return err(503,"No fue posible obtener los fragmentos de empleados.")
@router.post("",status_code=status.HTTP_201_CREATED)
def create_employee(d:EmployeeCreate)->dict[str,Any]:
 try:return {"success":True,"message":"Empleado registrado correctamente.","data":data(employee_service.create_employee(d))}
 except DatabaseConflictError:return err(409,"El ID o NIC ya existe.")
 except DatabaseError:return err(503,"No fue posible registrar el empleado.")
@router.put("/{id_empleado}/{id_sede}")
def update_employee(d:EmployeeUpdate,id_empleado:int=Path(gt=0),id_sede:Literal["001","002"]=Path())->dict[str,Any]:
 try:return {"success":True,"message":"Empleado actualizado correctamente.","data":data(employee_service.update_employee(id_empleado,id_sede,d))}
 except DatabaseNotFoundError:return err(404,"El empleado no existe.")
 except DatabaseConflictError:return err(409,"No se puede actualizar el empleado.")
 except DatabaseError:return err(503,"No fue posible actualizar el empleado.")
@router.delete("/{id_empleado}/{id_sede}")
def delete_employee(id_empleado:int=Path(gt=0),id_sede:Literal["001","002"]=Path())->dict[str,Any]:
 try:return {"success":True,"message":"Empleado eliminado correctamente.","data":data(employee_service.delete_employee(id_empleado,id_sede))}
 except DatabaseNotFoundError:return err(404,"El empleado no existe.")
 except DatabaseConflictError:return err(409,"No se puede eliminar el empleado porque tiene facturas relacionadas.")
 except DatabaseError:return err(503,"No fue posible eliminar el empleado.")
