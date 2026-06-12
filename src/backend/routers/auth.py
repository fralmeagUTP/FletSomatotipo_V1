from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Usuario
from ..auth_utils import verify_password, create_access_token
from ..audit import AuditService, get_client_ip
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    login_user: str
    user_id: int

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db), req: Request = None):
    """
    Autentica un usuario y genera un token de acceso.

    Args:
        request (LoginRequest): Credenciales del usuario (usuario y contraseña).
        db (Session): Sesión de base de datos.
        req (Request): Request HTTP para auditoría.

    Returns:
        dict: Token de acceso y detalles del usuario.
    
    Raises:
        HTTPException: Si las credenciales son inválidas.
    """
    # Metadatos para auditoría
    client_ip = get_client_ip(req) if req else 'unknown'
    user_agent = req.headers.get('User-Agent', '') if req else ''
    
    user = db.query(Usuario).filter(Usuario.LOGIN_USER == request.username).first()
    
    if not user:
        # Log login fallido - usuario no encontrado
        AuditService.log_action(
            db=db,
            action_code='LOGIN_FAILED',
            event_result='FAILURE',
            actor_login=request.username,
            http_method='POST',
            endpoint='/auth/login',
            status_code=401,
            client_ip=client_ip,
            user_agent=user_agent,
            error_message='Usuario no encontrado'
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    # Verify password (assuming plain text based on user context hint "passwords are in plain text")
    if user.PSW_USER != request.password:
        # Log login fallido - contraseña incorrecta
        AuditService.log_action(
            db=db,
            action_code='LOGIN_FAILED',
            event_result='FAILURE',
            actor_user_id=user.ID_USER,
            actor_login=request.username,
            http_method='POST',
            endpoint='/auth/login',
            status_code=401,
            client_ip=client_ip,
            user_agent=user_agent,
            error_message='Contraseña incorrecta'
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    access_token = create_access_token(data={"sub": user.LOGIN_USER, "id": user.ID_USER})
    
    # Log login exitoso
    AuditService.log_action(
        db=db,
        action_code='LOGIN_SUCCESS',
        event_result='SUCCESS',
        actor_user_id=user.ID_USER,
        actor_login=user.LOGIN_USER,
        http_method='POST',
        endpoint='/auth/login',
        status_code=200,
        client_ip=client_ip,
        user_agent=user_agent,
        response_json={
            'user_id': user.ID_USER,
            'username': user.NOM_USER,
            'login_user': user.LOGIN_USER
        }
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "username": user.NOM_USER,
        "login_user": user.LOGIN_USER,
        "user_id": user.ID_USER
    }
