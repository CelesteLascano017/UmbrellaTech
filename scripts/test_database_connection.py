"""Safe read-only diagnostic tool for the local SQL Server connection."""

from __future__ import annotations

import sys
from collections.abc import Sequence

import pyodbc

from app.core.config import get_settings
from app.core.database import DatabaseManager


def classify_odbc_error(error: pyodbc.Error) -> str:
    """Classify common ODBC failures without exposing secrets."""
    details = " ".join(str(item) for item in error.args).lower()
    sqlstate = str(error.args[0]) if error.args else ""
    if "data source name not found" in details or "driver" in details and "not found" in details:
        return "driver no instalado"
    if sqlstate in {"08001", "08S01"} or "error 53" in details or "server does not exist" in details:
        return "servidor no encontrado"
    if sqlstate == "28000" or "login failed" in details:
        return "autenticación rechazada"
    if "certificate" in details or "ssl" in details or "encryption" in details or "cifrado" in details:
        return "certificado/cifrado"
    if "cannot open database" in details or "database" in details and "does not exist" in details:
        return "base inexistente"
    if "timeout" in details or sqlstate == "HYT00":
        return "timeout"
    return "otro error ODBC"


def test_server(server: str) -> bool:
    """Run the read-only identity query against one local server alias."""
    settings = get_settings().model_copy(update={"db_server": server})
    database = DatabaseManager(settings)
    try:
        identity = database.fetch_one(
            "SELECT DB_NAME() AS database_name, @@SERVERNAME AS server_name;"
        )
        print(f"{server}: connected to {identity['database_name']} on {identity['server_name']}")
        return True
    except Exception as error:
        cause = error.__cause__
        if isinstance(cause, pyodbc.Error):
            print(f"{server}: {classify_odbc_error(cause)}")
        else:
            print(f"{server}: configuration or unexpected error")
        return False


def main(servers: Sequence[str]) -> int:
    settings = get_settings()
    print(f"Driver configured: {settings.db_driver}")
    if settings.db_driver not in pyodbc.drivers():
        print("Result: driver no instalado")
        return 1
    return 0 if any(test_server(server) for server in servers) else 1


if __name__ == "__main__":
    raise SystemExit(main(("DESKTOP-IMDA6IP", "localhost", ".", "(local)")))
