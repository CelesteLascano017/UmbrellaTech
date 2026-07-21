"""Read-only data access for product replication verification."""

import logging
from typing import Any

from app.core.database import DatabaseManager, database_manager
from app.core.exceptions import DatabaseError, DatabaseQueryError

logger = logging.getLogger(__name__)


class ReplicationRepository:
    """Queries the publisher and subscriber without changing either node."""

    _REMOTE_QUERY_TIMEOUT_SECONDS = 5

    def __init__(self, database: DatabaseManager = database_manager) -> None:
        self._database = database

    def check_local_node(self) -> dict[str, Any]:
        """Return the identity and availability of the local publisher node."""
        node = self._database.fetch_one(
            """
            SELECT
                '001' AS id_sede,
                'Tienda Floresta' AS nodo,
                @@SERVERNAME AS servidor,
                DB_NAME() AS base_datos,
                'Disponible' AS estado;
            """
        )
        if node is None:
            raise DatabaseQueryError("No fue posible comprobar el nodo local.")
        return node

    def check_remote_node(self) -> dict[str, Any]:
        """Verify that the linked server can read the subscriber table."""
        try:
            self._database.fetch_one(
                """
                SELECT TOP (1)
                    '002' AS id_sede,
                    'Tienda Sur' AS nodo,
                    'DUMDUM' AS servidor,
                    'TIENDA_SUR' AS base_datos,
                    'Disponible' AS estado
                FROM [DUMDUM].[TIENDA_SUR].[dbo].[Producto];
                """,
                query_timeout=self._REMOTE_QUERY_TIMEOUT_SECONDS,
            )
        except DatabaseError:
            logger.exception("No fue posible comprobar el nodo suscriptor mediante DUMDUM.")
            return self._remote_node("No disponible")
        return self._remote_node("Disponible")

    def get_local_product_count(self) -> int:
        """Return the number of products in Tienda Floresta."""
        result = self._database.fetch_one(
            """
            SELECT COUNT(*) AS productos_floresta
            FROM dbo.Producto;
            """
        )
        return self._count_from_result(result, "productos_floresta")

    def get_remote_product_count(self) -> int:
        """Return the number of products in Tienda Sur through DUMDUM."""
        result = self._database.fetch_one(
            """
            SELECT COUNT(*) AS productos_sur
            FROM [DUMDUM].[TIENDA_SUR].[dbo].[Producto];
            """,
            query_timeout=self._REMOTE_QUERY_TIMEOUT_SECONDS,
        )
        return self._count_from_result(result, "productos_sur")

    def get_product_replication_comparison(self) -> list[dict[str, Any]]:
        """Return the complete, read-only comparison of product records."""
        return self._database.fetch_all(
            """
            WITH ProductosFloresta AS
            (
                SELECT
                    id_producto,
                    nombre,
                    marca,
                    modelo,
                    descripcion,
                    precio
                FROM dbo.Producto
            ),
            ProductosSur AS
            (
                SELECT
                    id_producto,
                    nombre,
                    marca,
                    modelo,
                    descripcion,
                    precio
                FROM [DUMDUM].[TIENDA_SUR].[dbo].[Producto]
            )
            SELECT
                COALESCE(f.id_producto, s.id_producto) AS id_producto,
                f.nombre AS nombre_floresta,
                s.nombre AS nombre_sur,
                f.marca AS marca_floresta,
                s.marca AS marca_sur,
                f.modelo AS modelo_floresta,
                s.modelo AS modelo_sur,
                f.descripcion AS descripcion_floresta,
                s.descripcion AS descripcion_sur,
                f.precio AS precio_floresta,
                s.precio AS precio_sur,
                CASE
                    WHEN f.id_producto IS NULL THEN 'Solo existe en Sur'
                    WHEN s.id_producto IS NULL THEN 'Pendiente en Sur'
                    WHEN
                        ISNULL(f.nombre, '') = ISNULL(s.nombre, '')
                        AND ISNULL(f.marca, '') = ISNULL(s.marca, '')
                        AND ISNULL(f.modelo, '') = ISNULL(s.modelo, '')
                        AND ISNULL(f.descripcion, '') = ISNULL(s.descripcion, '')
                        AND ISNULL(f.precio, 0) = ISNULL(s.precio, 0)
                        THEN 'Sincronizado'
                    ELSE 'Datos diferentes'
                END AS estado
            FROM ProductosFloresta AS f
            FULL OUTER JOIN ProductosSur AS s
                ON s.id_producto = f.id_producto
            ORDER BY COALESCE(f.id_producto, s.id_producto);
            """,
            query_timeout=self._REMOTE_QUERY_TIMEOUT_SECONDS,
        )

    @staticmethod
    def _remote_node(estado: str) -> dict[str, str]:
        return {
            "id_sede": "002",
            "nodo": "Tienda Sur",
            "servidor": "DUMDUM",
            "base_datos": "TIENDA_SUR",
            "estado": estado,
        }

    @staticmethod
    def _count_from_result(result: dict[str, Any] | None, field: str) -> int:
        if result is None or result.get(field) is None:
            raise DatabaseQueryError("La consulta de productos no devolvió un conteo.")
        return int(result[field])
