"""HTTP API for read-only product replication status."""

from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.exceptions import DatabaseError
from app.services.replication_service import ReplicationService

router = APIRouter(prefix="/api/replication", tags=["Replication"])
replication_service = ReplicationService()


@router.get("/status")
def get_replication_status() -> Any:
    """Return node availability and product data consistency."""
    try:
        data = replication_service.get_replication_status()
    except DatabaseError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "message": "No fue posible consultar el nodo publicador.",
                "errors": {},
            },
        )

    message = "Estado de replicación obtenido correctamente."
    if data["estado_general"] == "No fue posible comprobar":
        message = "No fue posible comprobar el suscriptor."
    return {"success": True, "message": message, "data": data}
