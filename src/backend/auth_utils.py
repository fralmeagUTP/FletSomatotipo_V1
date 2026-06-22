from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .database import get_db
from .models import Usuario

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = max(1, int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    """
    Verifica si una contraseña en texto plano coincide con la contraseña hasheada.

    Args:
        plain_password (str): La contraseña en texto plano.
        hashed_password (str): La contraseña hasheada almacenada.

    Returns:
        bool: True si coinciden, False en caso contrario.
    """
    # In a real legacy DB scenario, passwords might not be hashed or use a different hash.
    # For now assuming standard bcrypt or plain comparison if needed (security risk, but depends on existing DB)
    # The user prompt mentions plain text passwords.
    return plain_password == hashed_password

def get_password_hash(password):
    """
    Genera el hash de una contraseña.

    Args:
        password (str): La contraseña a hashear.

    Returns:
        str: El hash de la contraseña.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Crea un token de acceso JWT.

    Args:
        data (dict): Los datos a codificar en el token (payload).
        expires_delta (Optional[timedelta]): Tiempo de expiración opcional.

    Returns:
        str: El token JWT codificado.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    """
    Decodifica un token JWT.

    Args:
        token (str): El token JWT a decodificar.

    Returns:
        dict | None: El payload decodificado si es válido, None en caso de error.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin usuario",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(Usuario).filter(Usuario.LOGIN_USER == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
