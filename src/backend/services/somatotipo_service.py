from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime
from decimal import Decimal

from ..models import Somatotipo, SomatotipoDetalle, VistaValoracionCorporal, Deportista, DeporteDeportista, Entidad, Deporte
from .pdf_service import build_longitudinal_pdf, build_valoracion_pdf
from .view_contract_service import EXPECTED_SOMATOTIPO_VIEW_COLUMNS


DUPLICATE_SOMATOTIPO_MESSAGE = (
    "Ya existe una valoración para este deportista en esa fecha. "
    "Agrega la toma como detalle de la valoración existente."
)


def create_somatotipo(db: Session, data):
    existing = (
        db.query(Somatotipo)
        .filter(
            Somatotipo.IDENTI_DEPORTISTA == data.IDENTI_DEPORTISTA,
            Somatotipo.FECHA_MEDIDA == data.FECHA_MEDIDA,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=DUPLICATE_SOMATOTIPO_MESSAGE,
        )

    try:
        header = Somatotipo(
            IDENTI_DEPORTISTA=data.IDENTI_DEPORTISTA,
            LOGIN_USER=data.LOGIN_USER,
            FECHA_MEDIDA=data.FECHA_MEDIDA,
            OBSERV=data.OBSERV,
        )
        db.add(header)
        db.flush()

        for detail in data.DETALLES:
            db.add(
                SomatotipoDetalle(
                    id_Somatotipo=header.id_Somatotipo,
                    **detail.model_dump(),
                )
            )

        db.commit()
        db.refresh(header)
        return {"message": "Somatotipo registrado con éxito", "id": header.id_Somatotipo}
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(status_code=409, detail=DUPLICATE_SOMATOTIPO_MESSAGE) from error
    except Exception:
        db.rollback()
        raise


def get_historial_somatotipos(db: Session, identi: str):
    return (
        db.query(Somatotipo)
        .options(joinedload(Somatotipo.detalles))
        .filter(Somatotipo.IDENTI_DEPORTISTA == identi)
        .all()
    )


def serialize_somatotipo_detail(detail: SomatotipoDetalle):
    return {
        "ID": detail.ID,
        "id_Somatotipo": detail.id_Somatotipo,
        "ESTA_USER_CM": float(detail.ESTA_USER_CM),
        "PESO_kg": float(detail.PESO_kg),
        "PLIEGUE_TRICIPITAL": float(detail.PLIEGUE_TRICIPITAL),
        "PLIEGUE_SUBESCAPULAR": float(detail.PLIEGUE_SUBESCAPULAR),
        "PLIEGUE_SUPRAILIACO": float(detail.PLIEGUE_SUPRAILIACO),
        "PLIEGUE_ABDOMINAL": float(detail.PLIEGUE_ABDOMINAL),
        "PLIEGUE_MUSLO_ANT": float(detail.PLIEGUE_MUSLO_ANT),
        "PLIEGUE_MEDIAL_PIERNA": float(detail.PLIEGUE_MEDIAL_PIERNA),
        "DIAMETRO_BIEPI_MUNECA": float(detail.DIAMETRO_BIEPI_MUNECA),
        "DIAMETRO_BIEPI_FEMUR": float(detail.DIAMETRO_BIEPI_FEMUR),
        "DIAMETRO_CODO": float(detail.DIAMETRO_CODO),
        "PERIMETRO_BICED_CONTRAIDO": float(detail.PERIMETRO_BICED_CONTRAIDO),
        "PERIMETRO_PIERNA": float(detail.PERIMETRO_PIERNA),
        "CIRCUNFERENCIA_CARPO": float(detail.CIRCUNFERENCIA_CARPO),
    }


def serialize_somatotipo_editable(somatotipo: Somatotipo):
    return {
        "id_Somatotipo": somatotipo.id_Somatotipo,
        "FECHA_MEDIDA": somatotipo.FECHA_MEDIDA.isoformat() if somatotipo.FECHA_MEDIDA else None,
        "IDENTI_DEPORTISTA": somatotipo.IDENTI_DEPORTISTA,
        "LOGIN_USER": somatotipo.LOGIN_USER,
        "OBSERV": somatotipo.OBSERV or "",
        "DETALLES": [serialize_somatotipo_detail(detail) for detail in somatotipo.detalles],
    }


def list_somatotipos_editables(db: Session, identi: str):
    records = (
        db.query(Somatotipo)
        .options(joinedload(Somatotipo.detalles))
        .filter(Somatotipo.IDENTI_DEPORTISTA == identi)
        .order_by(Somatotipo.FECHA_MEDIDA.desc(), Somatotipo.id_Somatotipo.desc())
        .all()
    )
    return [serialize_somatotipo_editable(record) for record in records]


def get_somatotipo_editable_or_404(db: Session, id_somatotipo: int):
    record = (
        db.query(Somatotipo)
        .options(joinedload(Somatotipo.detalles))
        .filter(Somatotipo.id_Somatotipo == id_somatotipo)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Valoración no encontrada")
    return serialize_somatotipo_editable(record)


def create_somatotipo_detalle(db: Session, id_somatotipo: int, data):
    somatotipo = db.query(Somatotipo).filter(Somatotipo.id_Somatotipo == id_somatotipo).first()
    if not somatotipo:
        raise HTTPException(status_code=404, detail="Valoración no encontrada")

    try:
        detail = SomatotipoDetalle(
            id_Somatotipo=id_somatotipo,
            **data.model_dump(),
        )
        db.add(detail)
        db.commit()
        db.refresh(detail)
        return serialize_somatotipo_detail(detail)
    except Exception:
        db.rollback()
        raise


def update_somatotipo_detalle(db: Session, detail_id: int, data):
    detail = db.query(SomatotipoDetalle).filter(SomatotipoDetalle.ID == detail_id).first()
    if not detail:
        raise HTTPException(status_code=404, detail="Medición no encontrada")

    try:
        for field, value in data.model_dump().items():
            setattr(detail, field, value)
        db.commit()
        db.refresh(detail)
        return serialize_somatotipo_detail(detail)
    except Exception:
        db.rollback()
        raise


def delete_somatotipo_detalle(db: Session, detail_id: int):
    detail = db.query(SomatotipoDetalle).filter(SomatotipoDetalle.ID == detail_id).first()
    if not detail:
        raise HTTPException(status_code=404, detail="Medición no encontrada")

    try:
        db.delete(detail)
        db.commit()
        return {"message": "Medición eliminada con éxito", "ID": detail_id}
    except Exception:
        db.rollback()
        raise


def get_historial_vista(db: Session, identi: str):
    records = (
        db.query(*vista_query_columns())
        .filter(VistaValoracionCorporal.IDENTI_DEPORTISTA == identi)
        .order_by(VistaValoracionCorporal.FECHA_MEDIDA.asc(), VistaValoracionCorporal.id_Somatotipo.asc())
        .all()
    )
    return [serialize_vista_record(record) for record in records]


def json_safe_value(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def vista_query_columns():
    return [
        getattr(VistaValoracionCorporal, column_name)
        for column_name in EXPECTED_SOMATOTIPO_VIEW_COLUMNS
        if hasattr(VistaValoracionCorporal, column_name)
    ]


def serialize_vista_record(record):
    source = getattr(record, "_mapping", None)
    return {
        column_name: json_safe_value(source[column_name] if source else getattr(record, column_name, None))
        for column_name in EXPECTED_SOMATOTIPO_VIEW_COLUMNS
        if (source and column_name in source) or hasattr(record, column_name)
    }


def get_historial_vista_page(db: Session, identi: str, page: int = 1, page_size: int = 20):
    query = db.query(*vista_query_columns()).filter(VistaValoracionCorporal.IDENTI_DEPORTISTA == identi)
    total = query.count()
    offset = (page - 1) * page_size
    items = (
        query.order_by(VistaValoracionCorporal.FECHA_MEDIDA.desc(), VistaValoracionCorporal.id_Somatotipo.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    return {
        "items": [serialize_vista_record(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_valoracion_vista_or_404(db: Session, id_somatotipo: int):
    record = (
        db.query(VistaValoracionCorporal)
        .filter(VistaValoracionCorporal.id_Somatotipo == id_somatotipo)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Valoración no encontrada")
    return record


def build_valoracion_pdf_response(db: Session, id_somatotipo: int):
    record = get_valoracion_vista_or_404(db, id_somatotipo)
    return build_valoracion_pdf(record)


def get_athlete_full_info(db: Session, identi: str):
    """
    Obtiene la información completa del deportista incluyendo entidades y deportes.
    """
    deportista = db.query(Deportista).filter(Deportista.IDENTI_DEPORTISTA == identi).first()
    if not deportista:
        return None
    
    # Calcular edad
    edad = None
    if deportista.FECHA_NAC:
        today = date.today()
        edad = today.year - deportista.FECHA_NAC.year - ((today.month, today.day) < (deportista.FECHA_NAC.month, deportista.FECHA_NAC.day))
    
    # Obtener deportes y entidades asociados
    asignaciones = (
        db.query(DeporteDeportista)
        .options(joinedload(DeporteDeportista.deporte), joinedload(DeporteDeportista.entidad))
        .filter(DeporteDeportista.IDENTI_DEPORTISTA == identi)
        .all()
    )
    
    deportes = []
    entidades = []
    for asig in asignaciones:
        if asig.deporte and asig.deporte.DEPORTE not in deportes:
            deportes.append(asig.deporte.DEPORTE)
        if asig.entidad and asig.entidad.RAZON_SOCIAL not in entidades:
            entidades.append(asig.entidad.RAZON_SOCIAL)
    
    return {
        "NOMBRE_DEPORTISTA": deportista.NOMBRE_DEPORTISTA,
        "IDENTI_DEPORTISTA": deportista.IDENTI_DEPORTISTA,
        "EDAD": edad,
        "SEXO_DEPORTISTA": deportista.SEXO_DEPORTISTA,
        "DIRECC_RESI": deportista.DIRECC_RESI,
        "CIUDAD_RESI": deportista.CIUDAD_RESI,
        "DEPARTA_RESI": deportista.DEPARTA_RESI,
        "E_MAIL": deportista.E_MAIL,
        "TELEFONO": deportista.TELEFONO,
        "DEPORTES": ", ".join(deportes) if deportes else "",
        "ENTIDADES": ", ".join(entidades) if entidades else "",
    }


def build_longitudinal_pdf_response(db: Session, identi: str):
    records = get_historial_vista(db, identi)
    if not records:
        raise HTTPException(status_code=404, detail="No hay valoraciones para generar el informe longitudinal")
    
    athlete_info = get_athlete_full_info(db, identi)
    return build_longitudinal_pdf(records, athlete_info)


def delete_somatotipo(db: Session, id_somatotipo: int):
    somatotipo = db.query(Somatotipo).filter(Somatotipo.id_Somatotipo == id_somatotipo).first()
    if not somatotipo:
        raise HTTPException(status_code=404, detail="Somatotipo no encontrado")

    try:
        db.query(SomatotipoDetalle).filter(SomatotipoDetalle.id_Somatotipo == id_somatotipo).delete()
        db.delete(somatotipo)
        db.commit()
        return {"message": "Somatotipo eliminado con éxito"}
    except Exception:
        db.rollback()
        raise
