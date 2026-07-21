"""Data access for distributed invoice details."""

from typing import Any

from app.core.database import DatabaseManager, database_manager
from app.core.exceptions import DatabaseConflictError, DatabaseNotFoundError, DatabaseQueryError
from app.schemas.invoice_detail import InvoiceDetailCreate, InvoiceDetailUpdate


class InvoiceDetailRepository:
    def __init__(self, database: DatabaseManager = database_manager) -> None: self._database = database
    def get_all_invoice_details(self) -> list[dict[str, Any]]:
        return self._database.fetch_all("""
            SELECT d.id_factura,d.id_sede,d.id_producto,p.nombre AS producto_nombre,d.num_linea,d.cantidad,d.precio_unitario,d.subtotal,f.fecha AS factura_fecha,f.total AS factura_total
            FROM dbo.vw_Detalle_Factura AS d
            INNER JOIN dbo.vw_Producto AS p ON p.id_producto=d.id_producto
            INNER JOIN dbo.vw_Factura AS f ON f.id_factura=d.id_factura AND f.id_sede=d.id_sede
            ORDER BY d.id_sede,d.id_factura,d.num_linea,d.id_producto;
        """)
    def create_invoice_detail(self,d:InvoiceDetailCreate)->dict[str,Any]: return self._execute("EXEC dbo.usp_DetalleFactura_Crear @id_factura=?,@id_sede=?,@id_producto=?,@num_linea=?,@cantidad=?,@precio_unitario=?;",(d.id_factura,d.id_sede,d.id_producto,d.num_linea,d.cantidad,d.precio_unitario),True)
    def update_invoice_detail(self,f:int,s:str,p:int,n:int,d:InvoiceDetailUpdate)->dict[str,Any]: return self._execute("EXEC dbo.usp_DetalleFactura_Actualizar @id_factura=?,@id_sede=?,@id_producto=?,@num_linea=?,@cantidad=?,@precio_unitario=?;",(f,s,p,n,d.cantidad,d.precio_unitario))
    def delete_invoice_detail(self,f:int,s:str,p:int,n:int)->dict[str,Any]: return self._execute("EXEC dbo.usp_DetalleFactura_Eliminar @id_factura=?,@id_sede=?,@id_producto=?,@num_linea=?;",(f,s,p,n))
    def _execute(self,q:str,params:tuple[Any,...],creating:bool=False)->dict[str,Any]:
        try: r=self._database.execute_and_fetch_one(q,params)
        except DatabaseQueryError as e:
            text=str(e.__cause__ or "").lower()
            if creating and any(x in text for x in ("2601","2627","duplicate","unique")): raise DatabaseConflictError("El detalle ya existe.") from e
            if "no existe" in text or "not found" in text: raise DatabaseNotFoundError("La factura, producto o detalle no existe.") from e
            raise
        if r is None or any(r.get(k) is None for k in ("id_factura","id_sede","id_producto","num_linea")): raise DatabaseQueryError("The stored procedure did not return detail identifiers.")
        return r
