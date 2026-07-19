from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.routers import pages

app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema Distribuido de Gestión para Umbrella Tech",
    version="1.0.0"
)

# Mount static files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(pages.router)
