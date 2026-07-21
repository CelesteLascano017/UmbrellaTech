from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "active_page": "dashboard"})

@router.get("/replicacion", response_class=HTMLResponse)
async def replicacion(request: Request):
    return templates.TemplateResponse("replicacion/index.html", {"request": request, "active_page": "replicacion"})

@router.get("/clientes", response_class=HTMLResponse)
async def clientes(request: Request):
    return templates.TemplateResponse("clientes/index.html", {"request": request, "active_page": "clientes"})

@router.get("/productos", response_class=HTMLResponse)
async def productos(request: Request):
    return templates.TemplateResponse("productos/index.html", {"request": request, "active_page": "productos"})

@router.get("/inventario", response_class=HTMLResponse)
async def inventario(request: Request):
    return templates.TemplateResponse("inventario/index.html", {"request": request, "active_page": "inventario"})

@router.get("/facturas", response_class=HTMLResponse)
async def facturas(request: Request):
    return templates.TemplateResponse("facturas/index.html", {"request": request, "active_page": "facturas"})

@router.get("/detalle-factura", response_class=HTMLResponse)
async def detalle_factura(request: Request):
    return templates.TemplateResponse("detalle_factura/index.html", {"request": request, "active_page": "facturas"})

@router.get("/empleados", response_class=HTMLResponse)
async def empleados(request: Request):
    return templates.TemplateResponse("empleados/index.html", {"request": request, "active_page": "empleados"})
