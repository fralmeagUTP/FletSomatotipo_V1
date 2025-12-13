from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Usuario
from ..auth_utils import verify_password, create_access_token
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    user_id: int

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica un usuario y genera un token de acceso.

    Args:
        request (LoginRequest): Credenciales del usuario (usuario y contraseña).
        db (Session): Sesión de base de datos.

    Returns:
        dict: Token de acceso y detalles del usuario.
    
    Raises:
        HTTPException: Si las credenciales son inválidas.
    """
    user = db.query(Usuario).filter(Usuario.LOGIN_USER == request.username).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    # Verify password (assuming plain text based on user context hint "passwords are in plain text")
    if user.PSW_USER != request.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    access_token = create_access_token(data={"sub": user.LOGIN_USER, "id": user.ID_USER})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "username": user.NOM_USER,
        "user_id": user.ID_USER
    }
