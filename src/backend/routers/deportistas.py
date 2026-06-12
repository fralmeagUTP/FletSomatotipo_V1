from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..auth_utils import get_current_user
from ..schemas.deportistas import DeportistaCreate, DeportistaPage, DeportistaResponse
from ..services import deportistas_service
from ..audit import AuditService, get_client_ip
from ..models import Usuario

router = APIRouter(prefix="/deportistas", tags=["Deportistas"], dependencies=[Depends(get_current_user)])

@router.get("/", response_model=DeportistaPage)
def listar_deportistas(
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    req: Request = None,
):
    """
    Lista los deportistas registrados, opcionalmente filtrando por nombre o identificación.

    Args:
        search (Optional[str]): Término de búsqueda (nombre o identificación).
        db (Session): Sesión de base de datos.
        req (Request): Request HTTP para auditoría.
    
    Returns:
        List[DeportistaResponse]: Lista de deportistas (máximo 50).
    """
    return deportistas_service.list_deportistas_page(db, search, page=max(page, 1), page_size=min(max(page_size, 1), 100))

@router.get("/{identi}", response_model=DeportistaResponse)
def obtener_deportista(identi: str, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de un deportista por su identificación.

    Args:
        identi (str): Identificación del deportista.
        db (Session): Sesión de base de datos.

    Returns:
        DeportistaResponse: Objeto deportista encontrado.

    Raises:
        HTTPException: Si el deportista no existe.
    """
    return deportistas_service.get_deportista_or_404(db, identi)

@router.post("/", response_model=DeportistaResponse)
def crear_deportista(d: DeportistaCreate, db: Session = Depends(get_db), req: Request = None):
    """
    Registra un nuevo deportista en el sistema.

    Args:
        d (DeportistaCreate): Datos del nuevo deportista.
        db (Session): Sesión de base de datos.
        req (Request): Request HTTP para auditoría.
    
    Returns:
        DeportistaResponse: El deportista creado.

    Raises:
        HTTPException: Si ya existe un deportista con la misma identificación.
    """
    client_ip = get_client_ip(req) if req else 'unknown'
    user_agent = req.headers.get('User-Agent', '') if req else ''
    
    # Obtener usuario autenticado
    actor_user_id = None
    actor_login = None
    try:
        user = get_current_user(req)
        actor_user_id = user.ID_USER
        actor_login = user.LOGIN_USER
    except:
        pass
    
    try:
        result = deportistas_service.create_deportista(db, d.model_dump())
        
        AuditService.log_action(
            db=db,
            action_code='CREATE_DEPORTISTA',
            event_result='SUCCESS',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='deportistas',
            resource_id=d.IDENTI_DEPORTISTA,
            http_method='POST',
            endpoint='/deportistas/',
            status_code=200,
            client_ip=client_ip,
            user_agent=user_agent,
            request_json={'IDENTI_DEPORTISTA': d.IDENTI_DEPORTISTA, 'NOMBRE_DEPORTISTA': d.NOMBRE_DEPORTISTA},
            response_json=result
        )
        
        return result
    except Exception as e:
        AuditService.log_action(
            db=db,
            action_code='CREATE_DEPORTISTA',
            event_result='FAILURE',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='deportistas',
            resource_id=d.IDENTI_DEPORTISTA,
            http_method='POST',
            endpoint='/deportistas/',
            status_code=500,
            client_ip=client_ip,
            user_agent=user_agent,
            request_json={'IDENTI_DEPORTISTA': d.IDENTI_DEPORTISTA},
            error_message=str(e)
        )
        raise

@router.put("/{identi}", response_model=DeportistaResponse)
def actualizar_deportista(identi: str, d: DeportistaCreate, db: Session = Depends(get_db), req: Request = None):
    """
    Actualiza los datos de un deportista existente.

    Args:
        identi (str): Identificación del deportista a actualizar.
        d (DeportistaCreate): Nuevos datos del deportista.
        db (Session): Sesión de base de datos.
        req (Request): Request HTTP para auditoría.

    Returns:
        DeportistaResponse: El deportista actualizado.

    Raises:
        HTTPException: Si el deportista no existe.
    """
    client_ip = get_client_ip(req) if req else 'unknown'
    user_agent = req.headers.get('User-Agent', '') if req else ''
    
    actor_user_id = None
    actor_login = None
    try:
        user = get_current_user(req)
        actor_user_id = user.ID_USER
        actor_login = user.LOGIN_USER
    except:
        pass
    
    try:
        result = deportistas_service.update_deportista(db, identi, d.model_dump())
        
        AuditService.log_action(
            db=db,
            action_code='UPDATE_DEPORTISTA',
            event_result='SUCCESS',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='deportistas',
            resource_id=identi,
            http_method='PUT',
            endpoint=f'/deportistas/{identi}',
            status_code=200,
            client_ip=client_ip,
            user_agent=user_agent,
            request_json={'NOMBRE_DEPORTISTA': d.NOMBRE_DEPORTISTA},
            response_json=result
        )
        
        return result
    except Exception as e:
        AuditService.log_action(
            db=db,
            action_code='UPDATE_DEPORTISTA',
            event_result='FAILURE',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='deportistas',
            resource_id=identi,
            http_method='PUT',
            endpoint=f'/deportistas/{identi}',
            status_code=500,
            client_ip=client_ip,
            user_agent=user_agent,
            error_message=str(e)
        )
        raise

@router.delete("/{identi}")
def eliminar_deportista(identi: str, db: Session = Depends(get_db), req: Request = None):
    """
    Elimina un deportista de la base de datos.
    
    Args:
        identi (str): Identificación del deportista a eliminar.
        db (Session): Sesión de base de datos.
        req (Request): Request HTTP para auditoría.

    Returns:
        dict: Mensaje de confirmación.

    Raises:
        HTTPException: Si el deportista no existe.
    """
    client_ip = get_client_ip(req) if req else 'unknown'
    user_agent = req.headers.get('User-Agent', '') if req else ''
    
    actor_user_id = None
    actor_login = None
    try:
        user = get_current_user(req)
        actor_user_id = user.ID_USER
        actor_login = user.LOGIN_USER
    except:
        pass
    
    # Obtener datos antes de eliminar para auditoría
    deportista = None
    try:
        deportista = deportistas_service.get_deportista_or_404(db, identi)
    except:
        pass
    
    try:
        result = deportistas_service.delete_deportista(db, identi)
        
        AuditService.log_action(
            db=db,
            action_code='DELETE_DEPORTISTA',
            event_result='SUCCESS',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='deportistas',
            resource_id=identi,
            http_method='DELETE',
            endpoint=f'/deportistas/{identi}',
            status_code=200,
            client_ip=client_ip,
            user_agent=user_agent,
            request_json={'IDENTI_DEPORTISTA': identi, 'NOMBRE': deportista.NOMBRE_DEPORTISTA if deportista else None},
            response_json=result
        )
        
        return result
    except Exception as e:
        AuditService.log_action(
            db=db,
            action_code='DELETE_DEPORTISTA',
            event_result='FAILURE',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='deportistas',
            resource_id=identi,
            http_method='DELETE',
            endpoint=f'/deportistas/{identi}',
            status_code=500,
            client_ip=client_ip,
            user_agent=user_agent,
            error_message=str(e)
        )
        raise
