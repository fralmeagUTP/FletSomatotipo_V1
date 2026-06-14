from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth_utils import get_current_user
from ..schemas.somatotipo import SomatotipoCreate, SomatotipoDetalleBase
from ..services import somatotipo_service, view_contract_service
from ..audit import AuditService, get_client_ip
from ..models import Usuario

router = APIRouter(prefix="/somatotipo", tags=["Somatotipo"], dependencies=[Depends(get_current_user)])


def audit_actor(current_user: Usuario):
    return getattr(current_user, "ID_USER", None), getattr(current_user, "LOGIN_USER", None)

@router.post("/")
def registrar_somatotipo(
    s: SomatotipoCreate,
    db: Session = Depends(get_db),
    req: Request = None,
    current_user: Usuario = Depends(get_current_user),
):
    """
    Registra un nuevo cálculo de somatotipo para un deportista.

    Guarda tanto el encabezado (fecha, observaciones) como el detalle (mediciones).

    Args:
        s (SomatotipoCreate): Datos del somatotipo y mediciones.
        db (Session): Sesión de base de datos.
        req (Request): Request HTTP para auditoría.

    Returns:
        dict: Mensaje de éxito e ID del nuevo registro.
    """
    client_ip = get_client_ip(req) if req else 'unknown'
    user_agent = req.headers.get('User-Agent', '') if req else ''
    
    actor_user_id, actor_login = audit_actor(current_user)
    
    try:
        result = somatotipo_service.create_somatotipo(db, s)
        
        AuditService.log_action(
            db=db,
            action_code='CREATE_SOMATOTIPO',
            event_result='SUCCESS',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='somatotipo',
            resource_id=str(result.get('id', '')),
            http_method='POST',
            endpoint='/somatotipo/',
            status_code=200,
            client_ip=client_ip,
            user_agent=user_agent,
            request_json={
                'IDENTI_DEPORTISTA': s.IDENTI_DEPORTISTA,
                'FECHA_MEDIDA': str(s.FECHA_MEDIDA),
                'DETALLES_COUNT': len(s.DETALLES)
            },
            response_json=result
        )
        
        return result
    except Exception as e:
        AuditService.log_action(
            db=db,
            action_code='CREATE_SOMATOTIPO',
            event_result='FAILURE',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='somatotipo',
            http_method='POST',
            endpoint='/somatotipo/',
            status_code=500,
            client_ip=client_ip,
            user_agent=user_agent,
            request_json={'IDENTI_DEPORTISTA': s.IDENTI_DEPORTISTA},
            error_message=str(e)
        )
        raise

@router.get("/deportista/{identi}")
def historial_somatotipos(identi: str, db: Session = Depends(get_db)):
    """
    Obtiene el historial de mediciones de somatotipo de un deportista.

    Args:
        identi (str): Identificación del deportista.
        db (Session): Sesión de base de datos.
    
    Returns:
        List[Somatotipo]: Lista de registros de somatotipo.
    """
    return somatotipo_service.get_historial_somatotipos(db, identi)
    
@router.get("/vista/deportista/{identi}")
def historial_vista(
    identi: str,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """
    Obtiene el historial de mediciones usando la VISTA CDRVistaValoracionCorporal.
    """
    return somatotipo_service.get_historial_vista_page(
        db,
        identi,
        page=max(page, 1),
        page_size=min(max(page_size, 1), 100),
    )


@router.get("/editable/deportista/{identi}")
def listar_valoraciones_editables(identi: str, db: Session = Depends(get_db)):
    """
    Lista valoraciones almacenadas con sus mediciones editables.
    """
    return somatotipo_service.list_somatotipos_editables(db, identi)


@router.get("/editable/{id_somatotipo}")
def cargar_valoracion_editable(id_somatotipo: int, db: Session = Depends(get_db)):
    """
    Carga una valoraciÃ³n almacenada con sus mediciones editables.
    """
    return somatotipo_service.get_somatotipo_editable_or_404(db, id_somatotipo)


@router.post("/{id_somatotipo}/detalle")
def crear_detalle_somatotipo(
    id_somatotipo: int,
    detalle: SomatotipoDetalleBase,
    db: Session = Depends(get_db),
    req: Request = None,
    current_user: Usuario = Depends(get_current_user),
):
    """
    Agrega una nueva toma/medición al detalle de una valoración existente.
    """
    client_ip = get_client_ip(req) if req else 'unknown'
    user_agent = req.headers.get('User-Agent', '') if req else ''
    
    actor_user_id, actor_login = audit_actor(current_user)
    
    try:
        result = somatotipo_service.create_somatotipo_detalle(db, id_somatotipo, detalle)
        
        AuditService.log_action(
            db=db,
            action_code='CREATE_SOMATOTIPO_DETALLE',
            event_result='SUCCESS',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='somatotipo_detalle',
            resource_id=str(id_somatotipo),
            http_method='POST',
            endpoint=f'/somatotipo/{id_somatotipo}/detalle',
            status_code=200,
            client_ip=client_ip,
            user_agent=user_agent,
            response_json=result
        )
        
        return result
    except Exception as e:
        AuditService.log_action(
            db=db,
            action_code='CREATE_SOMATOTIPO_DETALLE',
            event_result='FAILURE',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='somatotipo_detalle',
            resource_id=str(id_somatotipo),
            http_method='POST',
            endpoint=f'/somatotipo/{id_somatotipo}/detalle',
            status_code=500,
            client_ip=client_ip,
            user_agent=user_agent,
            error_message=str(e)
        )
        raise


@router.put("/detalle/{detalle_id}")
def actualizar_detalle_somatotipo(
    detalle_id: int,
    detalle: SomatotipoDetalleBase,
    db: Session = Depends(get_db),
    req: Request = None,
    current_user: Usuario = Depends(get_current_user),
):
    """
    Actualiza una mediciÃ³n antropomÃ©trica almacenada.
    """
    client_ip = get_client_ip(req) if req else 'unknown'
    user_agent = req.headers.get('User-Agent', '') if req else ''
    
    actor_user_id, actor_login = audit_actor(current_user)
    
    try:
        result = somatotipo_service.update_somatotipo_detalle(db, detalle_id, detalle)
        
        AuditService.log_action(
            db=db,
            action_code='UPDATE_SOMATOTIPO_DETALLE',
            event_result='SUCCESS',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='somatotipo_detalle',
            resource_id=str(detalle_id),
            http_method='PUT',
            endpoint=f'/somatotipo/detalle/{detalle_id}',
            status_code=200,
            client_ip=client_ip,
            user_agent=user_agent,
            response_json=result
        )
        
        return result
    except Exception as e:
        AuditService.log_action(
            db=db,
            action_code='UPDATE_SOMATOTIPO_DETALLE',
            event_result='FAILURE',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='somatotipo_detalle',
            resource_id=str(detalle_id),
            http_method='PUT',
            endpoint=f'/somatotipo/detalle/{detalle_id}',
            status_code=500,
            client_ip=client_ip,
            user_agent=user_agent,
            error_message=str(e)
        )
        raise


@router.delete("/detalle/{detalle_id}")
def eliminar_detalle_somatotipo(
    detalle_id: int,
    db: Session = Depends(get_db),
    req: Request = None,
    current_user: Usuario = Depends(get_current_user),
):
    """
    Elimina una toma/medición específica del detalle de una valoración.
    """
    client_ip = get_client_ip(req) if req else 'unknown'
    user_agent = req.headers.get('User-Agent', '') if req else ''
    
    actor_user_id, actor_login = audit_actor(current_user)
    
    try:
        result = somatotipo_service.delete_somatotipo_detalle(db, detalle_id)
        
        AuditService.log_action(
            db=db,
            action_code='DELETE_SOMATOTIPO_DETALLE',
            event_result='SUCCESS',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='somatotipo_detalle',
            resource_id=str(detalle_id),
            http_method='DELETE',
            endpoint=f'/somatotipo/detalle/{detalle_id}',
            status_code=200,
            client_ip=client_ip,
            user_agent=user_agent,
            response_json=result
        )
        
        return result
    except Exception as e:
        AuditService.log_action(
            db=db,
            action_code='DELETE_SOMATOTIPO_DETALLE',
            event_result='FAILURE',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='somatotipo_detalle',
            resource_id=str(detalle_id),
            http_method='DELETE',
            endpoint=f'/somatotipo/detalle/{detalle_id}',
            status_code=500,
            client_ip=client_ip,
            user_agent=user_agent,
            error_message=str(e)
        )
        raise


@router.get("/vista/contrato")
def contrato_vista_somatotipo(db: Session = Depends(get_db)):
    """
    Evalua si la vista SQL usada por historial conserva las columnas esperadas.
    """
    return view_contract_service.get_somatotipo_view_contract(db)


@router.get("/{id_somatotipo}/pdf")
def descargar_valoracion_pdf(
    id_somatotipo: int,
    db: Session = Depends(get_db),
    req: Request = None,
    current_user: Usuario = Depends(get_current_user),
):
    """
    Descarga los resultados de una valoración en formato PDF.
    """
    client_ip = get_client_ip(req) if req else 'unknown'
    user_agent = req.headers.get('User-Agent', '') if req else ''
    
    actor_user_id, actor_login = audit_actor(current_user)
    
    # Auditar descarga de PDF
    AuditService.log_action(
        db=db,
        action_code='DOWNLOAD_PDF_VALORACION',
        event_result='SUCCESS',
        actor_user_id=actor_user_id,
        actor_login=actor_login,
        resource_type='somatotipo_pdf',
        resource_id=str(id_somatotipo),
        http_method='GET',
        endpoint=f'/somatotipo/{id_somatotipo}/pdf',
        status_code=200,
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    pdf_bytes = somatotipo_service.build_valoracion_pdf_response(db, id_somatotipo)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="valoracion_{id_somatotipo}.pdf"'
        },
    )


@router.get("/vista/deportista/{identi}/longitudinal/pdf")
def descargar_analisis_longitudinal_pdf(
    identi: str,
    db: Session = Depends(get_db),
    req: Request = None,
    current_user: Usuario = Depends(get_current_user),
):
    """
    Descarga el análisis longitudinal del deportista en formato PDF.
    """
    client_ip = get_client_ip(req) if req else 'unknown'
    user_agent = req.headers.get('User-Agent', '') if req else ''
    
    actor_user_id, actor_login = audit_actor(current_user)
    
    # Auditar descarga de PDF longitudinal
    AuditService.log_action(
        db=db,
        action_code='DOWNLOAD_PDF_LONGITUDINAL',
        event_result='SUCCESS',
        actor_user_id=actor_user_id,
        actor_login=actor_login,
        resource_type='somatotipo_pdf_longitudinal',
        resource_id=identi,
        http_method='GET',
        endpoint=f'/somatotipo/vista/deportista/{identi}/longitudinal/pdf',
        status_code=200,
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    pdf_bytes = somatotipo_service.build_longitudinal_pdf_response(db, identi)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="analisis_longitudinal_{identi}.pdf"'
        },
    )


@router.delete("/{id_somatotipo}")
def delete_somatotipo(
    id_somatotipo: int,
    db: Session = Depends(get_db),
    req: Request = None,
    current_user: Usuario = Depends(get_current_user),
):
    """
    Elimina un registro de somatotipo y todos sus detalles asociados.
    """
    client_ip = get_client_ip(req) if req else 'unknown'
    user_agent = req.headers.get('User-Agent', '') if req else ''
    
    actor_user_id, actor_login = audit_actor(current_user)
    
    try:
        result = somatotipo_service.delete_somatotipo(db, id_somatotipo)
        
        AuditService.log_action(
            db=db,
            action_code='DELETE_SOMATOTIPO',
            event_result='SUCCESS',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='somatotipo',
            resource_id=str(id_somatotipo),
            http_method='DELETE',
            endpoint=f'/somatotipo/{id_somatotipo}',
            status_code=200,
            client_ip=client_ip,
            user_agent=user_agent,
            response_json=result
        )
        
        return result
    except Exception as e:
        AuditService.log_action(
            db=db,
            action_code='DELETE_SOMATOTIPO',
            event_result='FAILURE',
            actor_user_id=actor_user_id,
            actor_login=actor_login,
            resource_type='somatotipo',
            resource_id=str(id_somatotipo),
            http_method='DELETE',
            endpoint=f'/somatotipo/{id_somatotipo}',
            status_code=500,
            client_ip=client_ip,
            user_agent=user_agent,
            error_message=str(e)
        )
        raise
