"""Business logic for read-only product replication verification."""

import logging
from datetime import datetime
from typing import Any

from app.core.exceptions import DatabaseError
from app.repositories.replication_repository import ReplicationRepository

logger = logging.getLogger(__name__)


class ReplicationService:
    """Combines node availability and data consistency without copying records."""

    def __init__(self, repository: ReplicationRepository | None = None) -> None:
        self._repository = repository or ReplicationRepository()

    def get_replication_status(self) -> dict[str, Any]:
        """Build the replication status response from read-only repository results."""
        publicador = self._repository.check_local_node()
        productos_floresta = self._repository.get_local_product_count()
        suscriptor = self._repository.check_remote_node()
        ultima_comprobacion = datetime.now().isoformat(timespec="seconds")

        if suscriptor["estado"] != "Disponible":
            return self._unavailable_subscriber_status(
                publicador, suscriptor, productos_floresta, ultima_comprobacion
            )

        try:
            productos_sur = self._repository.get_remote_product_count()
            productos = self._repository.get_product_replication_comparison()
        except DatabaseError:
            logger.exception("El suscriptor dejó de estar disponible durante la comparación.")
            suscriptor = {**suscriptor, "estado": "No disponible"}
            return self._unavailable_subscriber_status(
                publicador, suscriptor, productos_floresta, ultima_comprobacion
            )

        resumen = {
            "productos_floresta": productos_floresta,
            "productos_sur": productos_sur,
            "sincronizados": sum(item["estado"] == "Sincronizado" for item in productos),
            "pendientes_sur": sum(item["estado"] == "Pendiente en Sur" for item in productos),
            "solo_sur": sum(item["estado"] == "Solo existe en Sur" for item in productos),
            "diferentes": sum(item["estado"] == "Datos diferentes" for item in productos),
        }
        hay_diferencias = any(
            resumen[field] > 0
            for field in ("pendientes_sur", "solo_sur", "diferentes")
        )
        return {
            "estado_general": (
                "Datos con diferencias" if hay_diferencias else "Datos sincronizados"
            ),
            "ultima_comprobacion": ultima_comprobacion,
            "publicador": publicador,
            "suscriptor": suscriptor,
            "resumen": resumen,
            "productos": productos,
        }

    @staticmethod
    def _unavailable_subscriber_status(
        publicador: dict[str, Any],
        suscriptor: dict[str, Any],
        productos_floresta: int,
        ultima_comprobacion: str,
    ) -> dict[str, Any]:
        return {
            "estado_general": "No fue posible comprobar",
            "ultima_comprobacion": ultima_comprobacion,
            "publicador": publicador,
            "suscriptor": suscriptor,
            "resumen": {
                "productos_floresta": productos_floresta,
                "productos_sur": None,
                "sincronizados": 0,
                "pendientes_sur": 0,
                "solo_sur": 0,
                "diferentes": 0,
            },
            "productos": [],
        }
