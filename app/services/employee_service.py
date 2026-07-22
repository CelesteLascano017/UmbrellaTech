"""Application service for employees."""
from typing import Any
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate,EmployeeUpdate
class EmployeeService:
 def __init__(self,repository:EmployeeRepository|None=None)->None:self._repository=repository or EmployeeRepository()
 def get_all_employees(self)->list[dict[str,Any]]:return self._repository.get_all_employees()
 def get_employee_fragments(self,s:str)->dict[str,list[dict[str,Any]]]:
  self._valid_branch(s)
  if s=="001":return {"admin":self._repository.get_admin_employees_001(),"payroll":self._repository.get_payroll_employees()}
  return {"admin":self._repository.get_admin_employees_002(),"payroll":[]}
 def create_employee(self,d:EmployeeCreate)->dict[str,Any]:self._valid(d.id_empleado,d.id_sede,d.edad,d.sueldo);return self._repository.create_employee(d)
 def update_employee(self,i:int,s:str,d:EmployeeUpdate)->dict[str,Any]:self._valid(i,s,d.edad,d.sueldo);return self._repository.update_employee(i,s,d)
 def delete_employee(self,i:int,s:str)->dict[str,Any]:self._valid(i,s);return self._repository.delete_employee(i,s)
 @staticmethod
 def _valid(i:int,s:str,age:int|None=None,salary:Any=None)->None:
  if i<=0 or s not in {"001","002"}:raise ValueError("Invalid employee identity.")
  if age is not None and age<0:raise ValueError("Invalid age.")
  if salary is not None and salary<0:raise ValueError("Invalid salary.")
 @staticmethod
 def _valid_branch(s:str)->None:
  if s not in {"001","002"}:raise ValueError("Invalid employee branch.")
