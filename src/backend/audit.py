"""
Módulo de Auditoría - SomatoCarta
Sistema completo de logging y auditoría de operaciones
"""
import logging
import json
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Optional, Dict, Any, Callable
from fastapi import Request, Response
from sqlalchemy.orm import Session

from src.backend.database import get_db

# Configurar logger de auditoría
audit_logger = logging.getLogger('somatocarta.audit')
audit_logger.setLevel(logging.INFO)

# Handler para archivo de log
file_handler = logging.FileHandler('audit.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# Formato de log
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

audit_logger.addHandler(file_handler)
audit_logger.addHandler(console_handler)


class AuditService:
    """Servicio de auditoría para registrar operaciones"""
    
    @staticmethod
    def log_action(
        db: Session,
        action_code: str,
        event_result: str,
        actor_user_id: Optional[int] = None,
        actor_login: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        http_method: Optional[str] = None,
        endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        correlation_id: Optional[str] = None,
        request_json: Optional[Dict[str, Any]] = None,
        response_json: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """
        Registra una acción de auditoría en la base de datos y en logs
        
        Args:
            db: Sesión de base de datos
            action_code: Código de la acción (ej: LOGIN_SUCCESS, CREATE_DEPORTISTA)
            event_result: Resultado del evento (SUCCESS, FAILURE, ERROR)
            actor_user_id: ID del usuario que realizó la acción
            actor_login: Login del usuario
            resource_type: Tipo de recurso (deportistas, valoraciones, etc.)
            resource_id: ID del recurso afectado
            http_method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint llamado
            status_code: Código de estado HTTP
            client_ip: IP del cliente
            user_agent: User agent del cliente
            correlation_id: ID de correlación para tracking
            request_json: Datos del request en JSON
            response_json: Datos del response en JSON
            error_message: Mensaje de error si ocurrió
        """
        try:
            # Crear registro de auditoría
            audit_record = {
                'OCCURRED_AT_UTC': datetime.now(timezone.utc),
                'ACTOR_USER_ID': actor_user_id,
                'ACTOR_LOGIN': actor_login,
                'ACTION_CODE': action_code,
                'RESOURCE_TYPE': resource_type,
                'RESOURCE_ID': resource_id,
                'EVENT_RESULT': event_result,
                'HTTP_METHOD': http_method,
                'ENDPOINT': endpoint,
                'STATUS_CODE': status_code,
                'CLIENT_IP': client_ip,
                'USER_AGENT': user_agent,
                'CORRELATION_ID': correlation_id or str(uuid.uuid4()),
                'REQUEST_JSON': json.dumps(request_json, ensure_ascii=False, default=str) if request_json else None,
                'RESPONSE_JSON': json.dumps(response_json, ensure_ascii=False, default=str) if response_json else None,
                'ERROR_MESSAGE': error_message
            }
            
            # Insertar en base de datos
            from src.backend.models import Auditoria
            audit_entry = Auditoria(**audit_record)
            db.add(audit_entry)
            db.commit()
            
            # Log en archivo
            audit_logger.info(json.dumps({
                'action': action_code,
                'result': event_result,
                'user': actor_login,
                'resource': f"{resource_type}:{resource_id}" if resource_type else None,
                'endpoint': endpoint,
                'status': status_code,
                'ip': client_ip
            }, ensure_ascii=False))
            
        except Exception as e:
            # Si falla la auditoría, loguear el error pero no interrumpir la operación
            audit_logger.error(f"Error al registrar auditoría: {str(e)}")
            try:
                db.rollback()
            except:
                pass


def get_client_ip(request: Request) -> str:
    """Obtiene la IP del cliente desde el request"""
    # Verificar headers de proxy
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else 'unknown'


def audit_endpoint(action_code: str, resource_type: str):
    """
    Decorador para auditar endpoints automáticamente
    
    Args:
        action_code: Código de la acción (ej: CREATE_DEPORTISTA)
        resource_type: Tipo de recurso (ej: deportistas)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Obtener request y db del contexto
            request = kwargs.get('request')
            db = kwargs.get('db')
            
            # Si no hay request o db, ejecutar normalmente
            if not request or not db:
                return await func(*args, **kwargs)
            
            # Generar correlation ID
            correlation_id = str(uuid.uuid4())
            
            # Extraer información del request
            client_ip = get_client_ip(request)
            user_agent = request.headers.get('User-Agent', '')
            http_method = request.method
            endpoint = str(request.url.path)
            
            # Intentar obtener usuario autenticado
            actor_user_id = None
            actor_login = None
            try:
                from src.backend.auth_utils import get_current_user
                user = await get_current_user(request)
                if user:
                    actor_user_id = user.ID_USER
                    actor_login = user.LOGIN_USER
            except:
                pass
            
            # Capturar request body si existe
            request_json = None
            try:
                body = await request.json()
                # No loguear contraseñas
                if 'password' in body:
                    body['password'] = '***'
                request_json = body
            except:
                pass
            
            # Ejecutar la función
            start_time = datetime.now()
            status_code = 200
            event_result = 'SUCCESS'
            error_message = None
            response_json = None
            
            try:
                result = await func(*args, **kwargs)
                
                # Extraer response
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                if hasattr(result, 'body'):
                    try:
                        response_json = json.loads(result.body)
                    except:
                        pass
                elif isinstance(result, dict):
                    response_json = result
                    status_code = 200
                
                # Determinar resultado
                if status_code >= 400:
                    event_result = 'FAILURE'
                    
            except Exception as e:
                event_result = 'ERROR'
                error_message = str(e)
                status_code = 500
                raise
            finally:
                # Registrar en auditoría
                AuditService.log_action(
                    db=db,
                    action_code=action_code,
                    event_result=event_result,
                    actor_user_id=actor_user_id,
                    actor_login=actor_login,
                    resource_type=resource_type,
                    http_method=http_method,
                    endpoint=endpoint,
                    status_code=status_code,
                    client_ip=client_ip,
                    user_agent=user_agent,
                    correlation_id=correlation_id,
                    request_json=request_json,
                    response_json=response_json,
                    error_message=error_message
                )
            
            return result
        return wrapper
    return decorator


# Funciones helper para auditoría manual
def log_login_success(db: Session, user_id: int, login: str, ip: str, user_agent: str):
    """Registra un login exitoso"""
    AuditService.log_action(
        db=db,
        action_code='LOGIN_SUCCESS',
        event_result='SUCCESS',
        actor_user_id=user_id,
        actor_login=login,
        http_method='POST',
        endpoint='/auth/login',
        status_code=200,
        client_ip=ip,
        user_agent=user_agent
    )


def log_login_failure(db: Session, login: str, ip: str, user_agent: str, reason: str):
    """Registra un login fallido"""
    AuditService.log_action(
        db=db,
        action_code='LOGIN_FAILED',
        event_result='FAILURE',
        actor_login=login,
        http_method='POST',
        endpoint='/auth/login',
        status_code=401,
        client_ip=ip,
        user_agent=user_agent,
        error_message=reason
    )


def log_logout(db: Session, user_id: int, login: str, ip: str):
    """Registra un logout"""
    AuditService.log_action(
        db=db,
        action_code='LOGOUT',
        event_result='SUCCESS',
        actor_user_id=user_id,
        actor_login=login,
        http_method='POST',
        endpoint='/auth/logout',
        status_code=200,
        client_ip=ip
    )


def log_crud_operation(
    db: Session,
    action: str,  # CREATE, UPDATE, DELETE
    resource_type: str,
    resource_id: str,
    user_id: int,
    user_login: str,
    endpoint: str,
    status_code: int,
    ip: str,
    request_data: Optional[Dict] = None,
    response_data: Optional[Dict] = None,
    error: Optional[str] = None
):
    """Registra una operación CRUD"""
    action_code = f'{action}_{resource_type.upper()}'
    event_result = 'SUCCESS' if status_code < 400 else 'FAILURE'
    
    AuditService.log_action(
        db=db,
        action_code=action_code,
        event_result=event_result,
        actor_user_id=user_id,
        actor_login=user_login,
        resource_type=resource_type,
        resource_id=resource_id,
        http_method='POST' if action == 'CREATE' else ('PUT' if action == 'UPDATE' else 'DELETE'),
        endpoint=endpoint,
        status_code=status_code,
        client_ip=ip,
        request_json=request_data,
        response_json=response_data,
        error_message=error
    )
