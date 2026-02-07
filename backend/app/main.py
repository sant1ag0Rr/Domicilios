"""
Aplicación principal FastAPI - MVP Delivery Local

Arquitectura Refactorizada:
- Backend: API REST (FastAPI) en carpeta `backend/`
- Frontend: React SPA (Vite) en carpeta `frontend/dist/` (build)
- Integración: El Backend sirve el build de React como archivos estáticos.
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from app.websockets import manager

# ... imports anteriores ...
# Importar rutas
# Se asume que se ejecuta desde la carpeta `backend` o con PYTHONPATH configurado
from app.routes import delivery, payments, couriers, notifications, auth

# ... Configuración de rutas de archivos ...
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR) # Root del proyecto
# Apuntar a la carpeta 'dist' generada por 'npm run build'
FRONTEND_DIST_DIR = os.path.join(PROJECT_ROOT, "frontend", "dist")
ASSETS_DIR = os.path.join(FRONTEND_DIST_DIR, "assets")

app = FastAPI(
    title="MVP Delivery Local API",
    description="API REST para el sistema de delivery",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS (Permitir que el frontend acceda si estuviera en otro servidor)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint WebSocket
@app.websocket("/ws/orders/{order_id}")
async def websocket_endpoint(websocket: WebSocket, order_id: int):
    await manager.connect(websocket, order_id)
    try:
        while True:
            await websocket.receive_text()
            # Aquí podríamos recibir mensajes del cliente si fuera necesario
    except WebSocketDisconnect:
        manager.disconnect(websocket, order_id)

# 2. Registrar rutas de la API
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(delivery.router, prefix="/api/delivery", tags=["Delivery"])
app.include_router(payments.router, prefix="/api/payments", tags=["Pagos"])
app.include_router(couriers.router, prefix="/api/couriers", tags=["Repartidores"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notificaciones"])

# 3. Servir Frontend (React SPA)
# Primero montar los assets de Vite
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# Ruta SPA catch-all: Cualquier ruta que no sea API devuelve index.html
# Esto permite que React Router maneje la navegación en el cliente
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Si la ruta comienza con api, dejar pasar (debería haber sido capturada antes si existe, o 404 si no)
    # Pero FastAPI ejecuta esto en orden. Las rutas de API están incluidas antes, así que tienen prioridad.
    if full_path.startswith("api"):
        return JSONResponse(status_code=404, content={"message": "Endpoint no encontrado"})
    
    # Servir index.html para cualquier otra ruta (SPA)
    index_path = os.path.join(FRONTEND_DIST_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Frontend no construido. Ejecuta 'npm run build' en la carpeta frontend."}

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0"}

if __name__ == "__main__":
    # Ejecutar servidor
    uvicorn.run(app, host="0.0.0.0", port=8000)
