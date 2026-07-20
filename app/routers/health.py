"""HTTP endpoints for application and database availability."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import DatabaseError
from app.core.health_checks import database_health_checker

router = APIRouter(prefix="/health", tags=["Health"])


def _service_unavailable(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"success": False, "message": message, "errors": {}},
    )


@router.get("")
def application_health() -> dict[str, object]:
    return {"success": True, "application": get_settings().app_name}


@router.get("/database")
def database_health() -> dict[str, object]:
    try:
        identity = database_health_checker.database_identity()
        return {
            "success": True,
            "message": "Conexión con SQL Server establecida",
            "data": {
                "database": identity["database_name"],
                "server": identity["server_name"],
            },
        }
    except (DatabaseError, KeyError):
        return _service_unavailable("La base de datos no está disponible.")


@router.get("/distributed-views")
def distributed_views_health() -> dict[str, object]:
    views = database_health_checker.distributed_views()
    if not all(views.values()):
        return _service_unavailable("Una o más vistas distribuidas no están disponibles.")
    return {"success": True, "views": views}


@router.get("/linked-server")
def linked_server_health() -> dict[str, object]:
    try:
        database_health_checker.linked_server()
        return {"success": True, "linked_server": "DUMDUM", "status": "connected"}
    except DatabaseError:
        return _service_unavailable("El servidor vinculado no está disponible.")
