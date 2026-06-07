from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import os
import uuid
from ..auth_utils import get_current_user

router = APIRouter(
    prefix="/files",
    tags=["files"],
    dependencies=[Depends(get_current_user)]
)

UPLOAD_DIR = "src/backend/static/uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024

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
        file_extension = os.path.splitext(file.filename or "")[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Solo se permiten imagenes JPG o PNG")

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen JPG o PNG")

        os.makedirs(UPLOAD_DIR, exist_ok=True)

        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        written = 0

        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                written += len(chunk)
                if written > MAX_UPLOAD_SIZE:
                    buffer.close()
                    os.remove(file_path)
                    raise HTTPException(status_code=400, detail="La imagen no puede superar 5 MB")
                buffer.write(chunk)

        return {"url": f"/static/uploads/{filename}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
