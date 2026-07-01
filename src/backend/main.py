import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import engine, get_db, Base
from . import models
from fastapi.staticfiles import StaticFiles
from .routers import auth, catalogos, dashboard, deportistas, entidades_deportes, files, somatotipo

app = FastAPI()

allowed_origins = [
    origin.strip()
    for origin in os.getenv("WEB_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

# Mount Static Files
app.mount("/static", StaticFiles(directory="src/backend/static"), name="static")

app.include_router(auth.router)
app.include_router(deportistas.router)
app.include_router(somatotipo.router)
app.include_router(catalogos.router)
app.include_router(files.router)
app.include_router(dashboard.router)
app.include_router(entidades_deportes.router)

# Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    """
    Ruta raíz de la API.
    
    Returns:
        dict: Mensaje de confirmación de ejecución.
    """
    return {"message": "Somatotipo API is running"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Endpoint de verificación de estado (Health Check).

    Verifica la conexión a la base de datos realizando una consulta simple.

    Args:
        db (Session): Sesión de base de datos.
    
    Returns:
        dict: Estado de la aplicación y de la base de datos.
    """
    try:
        # Test connection
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
