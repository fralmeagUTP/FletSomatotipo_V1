from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid

router = APIRouter(
    prefix="/files",
    tags=["files"]
)

UPLOAD_DIR = "src/backend/static/uploads"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Sube un archivo al servidor.

    Genera un nombre único para el archivo y lo guarda en el directorio de uploads.

    Args:
        file (UploadFile): El archivo a subir.

    Returns:
        dict: URL relativa del archivo subido.

    Raises:
        HTTPException: Si ocurre un error durante la carga.
    """
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Return relative URL
        return {"url": f"/static/uploads/{filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
