"""Application service for invoice details."""
from typing import Any
from app.repositories.invoice_detail_repository import InvoiceDetailRepository
from app.schemas.invoice_detail import InvoiceDetailCreate,InvoiceDetailUpdate
class InvoiceDetailService:
 def __init__(self,repository:InvoiceDetailRepository|None=None)->None:self._repository=repository or InvoiceDetailRepository()
 def get_all_invoice_details(self)->list[dict[str,Any]]:return self._repository.get_all_invoice_details()
 def create_invoice_detail(self,d:InvoiceDetailCreate)->dict[str,Any]:self._validate(d.id_factura,d.id_sede,d.id_producto,d.num_linea,d.cantidad,d.precio_unitario);return self._repository.create_invoice_detail(d)
 def update_invoice_detail(self,f:int,s:str,p:int,n:int,d:InvoiceDetailUpdate)->dict[str,Any]:self._validate(f,s,p,n,d.cantidad,d.precio_unitario);return self._repository.update_invoice_detail(f,s,p,n,d)
 def delete_invoice_detail(self,f:int,s:str,p:int,n:int)->dict[str,Any]:self._validate(f,s,p,n);return self._repository.delete_invoice_detail(f,s,p,n)
 @staticmethod
 def _validate(f:int,s:str,p:int,n:int,q:int|None=None,price:Any=None)->None:
  if f<=0 or p<=0 or n<=0 or s not in {"001","002"}:raise ValueError("Invalid detail identity.")
  if q is not None and q<=0:raise ValueError("Invalid quantity.")
  if price is not None and price<0:raise ValueError("Invalid unit price.")
