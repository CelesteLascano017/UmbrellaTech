# Umbrella Tech - Sistema Distribuido de Gestión

Este proyecto es la capa de presentación y lógica de negocio para el sistema de Umbrella Tech, el cual consume una base de datos distribuida en SQL Server.

## Características
- Desarrollado con FastAPI y Python.
- Arquitectura limpia (Clean Architecture, SOLID, Repository Pattern).
- Diseño responsivo con Bootstrap 5 y CSS personalizado.
- Conexión a SQL Server mediante pyodbc.

## Requisitos previos
- Python 3.10+
- SQL Server (y ODBC Driver 17 for SQL Server o superior instalado en el equipo).

## Configuración del entorno local
1. Clona el repositorio.
2. Crea un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Copia el archivo de variables de entorno y ajusta las credenciales:
   ```bash
   cp .env.example .env
   ```
5. Ejecuta la aplicación:
   ```bash
   uvicorn app.main:app --reload
   ```

## Arquitectura de la Base de Datos
El proyecto consume vistas distribuidas (ej. `vw_Cliente`, `vw_Producto`) ubicadas en SQL Server. La aplicación desconoce la fragmentación horizontal y vertical, tratando con la base de datos como una única entidad gracias a los Linked Servers ya implementados en el motor de DB.
