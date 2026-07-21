from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import get_settings
from app.core.logging_config import configure_logging
from app.routers import clients, health, pages, products

configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Sistema Distribuido de Gestión para Umbrella Tech",
    version="1.0.0"
)

# Mount static files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(health.router)
app.include_router(clients.router)
app.include_router(products.router)
