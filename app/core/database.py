import pyodbc
from app.core.config import settings

def get_db_connection():
    """
    Returns a new pyodbc connection to the SQL Server database.
    Configuration is driven by environment variables.
    
    Raises:
        Exception: If connection fails or variables are not set properly.
    """
    if not all([settings.DB_SERVER, settings.DB_DATABASE]):
        raise ValueError("Database configuration is incomplete in the environment variables.")
        
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={settings.DB_SERVER};"
        f"DATABASE={settings.DB_DATABASE};"
        f"UID={settings.DB_USER};"
        f"PWD={settings.DB_PASSWORD};"
    )
    
    return pyodbc.connect(connection_string)

def get_db():
    """
    Dependency generator that yields a database connection.
    Ensures connection is closed after the request is processed.
    """
    conn = None
    try:
        # conn = get_db_connection() # Commented out until we actually connect
        yield conn
    finally:
        if conn:
            conn.close()
