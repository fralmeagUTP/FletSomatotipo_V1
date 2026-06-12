from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import engine, get_db, Base
from . import models
from fastapi.staticfiles import StaticFiles
from .routers import auth, catalogos, dashboard, deportistas, entidades_deportes, files, somatotipo

app = FastAPI()

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
