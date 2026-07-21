"""HTTP API for invoice details."""
from typing import Any,Literal
from fastapi import APIRouter,Path,status
from fastapi.responses import JSONResponse
from app.core.exceptions import DatabaseConflictError,DatabaseError,DatabaseNotFoundError
from app.schemas.invoice_detail import InvoiceDetailCreate,InvoiceDetailUpdate
from app.services.invoice_detail_service import InvoiceDetailService
router=APIRouter(prefix="/api/invoice-details",tags=["Invoice details"]); invoice_detail_service=InvoiceDetailService()
def err(c:int,m:str)->JSONResponse:return JSONResponse(status_code=c,content={"success":False,"message":m,"errors":{}})
def data(r:dict[str,Any])->dict[str,Any]:return {k:r[k] for k in ("id_factura","id_sede","id_producto","num_linea")}
@router.get("")
def get_all_invoice_details()->dict[str,Any]:
 try:return {"success":True,"message":"Detalles de factura obtenidos correctamente.","data":invoice_detail_service.get_all_invoice_details()}
 except DatabaseError:return err(503,"No fue posible obtener los detalles de factura.")
@router.post("",status_code=status.HTTP_201_CREATED)
def create_invoice_detail(d:InvoiceDetailCreate)->dict[str,Any]:
 try:return {"success":True,"message":"Detalle de factura registrado correctamente.","data":data(invoice_detail_service.create_invoice_detail(d))}
 except DatabaseConflictError:return err(409,"El detalle de factura ya existe.")
 except DatabaseNotFoundError:return err(404,"La factura o producto no existe.")
 except DatabaseError:return err(503,"No fue posible registrar el detalle de factura.")
@router.put("/{id_factura}/{id_sede}/{id_producto}/{num_linea}")
def update_invoice_detail(d:InvoiceDetailUpdate,id_factura:int=Path(gt=0),id_sede:Literal["001","002"]=Path(),id_producto:int=Path(gt=0),num_linea:int=Path(gt=0))->dict[str,Any]:
 try:return {"success":True,"message":"Detalle de factura actualizado correctamente.","data":data(invoice_detail_service.update_invoice_detail(id_factura,id_sede,id_producto,num_linea,d))}
 except DatabaseNotFoundError:return err(404,"El detalle de factura no existe.")
 except DatabaseError:return err(503,"No fue posible actualizar el detalle de factura.")
@router.delete("/{id_factura}/{id_sede}/{id_producto}/{num_linea}")
def delete_invoice_detail(id_factura:int=Path(gt=0),id_sede:Literal["001","002"]=Path(),id_producto:int=Path(gt=0),num_linea:int=Path(gt=0))->dict[str,Any]:
 try:return {"success":True,"message":"Detalle de factura eliminado correctamente.","data":data(invoice_detail_service.delete_invoice_detail(id_factura,id_sede,id_producto,num_linea))}
 except DatabaseNotFoundError:return err(404,"El detalle de factura no existe.")
 except DatabaseError:return err(503,"No fue posible eliminar el detalle de factura.")
