import os

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from .database import Base

class TipoUser(Base):
    """
    Modelo que mapea a la tabla CDRTablaTipoUser.
    Catálogo de tipos de usuario (roles).
    """
    __tablename__ = "CDRTablaTipoUser"
    id_Tipo_User = Column(Integer, primary_key=True)
    Tipo_User = Column(String(100))

class Usuario(Base):
    """
    Modelo que mapea a la tabla CDRTablaUsuarios.
    Almacena la información de los usuarios del sistema.
    """
    __tablename__ = "CDRTablaUsuarios"
    ID_USER = Column(Integer, primary_key=True, autoincrement=True)
    LOGIN_USER = Column(String(60), unique=True)
    PSW_USER = Column(String(50))
    NOM_USER = Column(String(255))
    MAIL_USER = Column(String(255))
    ID_TIPO_USER = Column(Integer, ForeignKey("CDRTablaTipoUser.id_Tipo_User"))
    TELEFONO_USER = Column(String(20))
    DIRECC_USER = Column(String(100))
    
    tipo_usuario = relationship("TipoUser")

class TipoDocumento(Base):
    """
    Modelo que mapea a la tabla CDRTablaTipoDocumento.
    Catálogo de tipos de documentos de identidad.
    """
    __tablename__ = "CDRTablaTipoDocumento"
    TIPO_IDENTI = Column(Integer, primary_key=True)
    NOMBRE_IDENTI = Column(String(50))

class Estrato(Base):
    """
    Modelo que mapea a la tabla CDRTablaEstrato.
    Catálogo de estratos socioeconómicos.
    """
    __tablename__ = "CDRTablaEstrato"
    ID_ESTRATO = Column(Integer, primary_key=True)
    ESTRATO = Column(String(50))

class NivelEducativo(Base):
    """
    Modelo que mapea a la tabla CDRTablaNivelEducativo.
    Catálogo de niveles educativos.
    """
    __tablename__ = "CDRTablaNivelEducativo"
    ID_NIVEL = Column(Integer, primary_key=True)
    NIVEL_EDUCATIVO = Column(String(50))

class Deportista(Base):
    """
    Modelo que mapea a la tabla CDRTablaDeportistas.
    Almacena la información personal y demográfica de los deportistas.
    """
    __tablename__ = "CDRTablaDeportistas"
    IDENTI_DEPORTISTA = Column(String(20), primary_key=True)
    TIPO_IDENTI = Column(Integer, ForeignKey("CDRTablaTipoDocumento.TIPO_IDENTI"))
    NOMBRE_DEPORTISTA = Column(String(50))
    FOTO_DEPORTISTA = Column(String(2000))
    SEXO_DEPORTISTA = Column(String(1))
    PAIS_NAC = Column(String(30))
    DEPARTA_NAC = Column(String(30))
    CIUDAD_NAC = Column(String(30))
    FECHA_NAC = Column(Date)
    DEPARTA_RESI = Column(String(30))
    CIUDAD_RESI = Column(String(30))
    ID_ESTRATO = Column(Integer, ForeignKey("CDRTablaEstrato.ID_ESTRATO"))
    DIRECC_RESI = Column(String(50))
    TELEFONO = Column(String(20))
    E_MAIL = Column(String(50))
    ID_NIVEL = Column(Integer, ForeignKey("CDRTablaNivelEducativo.ID_NIVEL"))
    NOMBRE_INSTITU = Column(String(50))
    OBSERVACIONES = Column(Text)

    tipo_documento = relationship("TipoDocumento")
    estrato = relationship("Estrato")
    nivel_educativo = relationship("NivelEducativo")


class Entidad(Base):
    """
    Modelo que mapea a la tabla CDRTablaEntidades.
    Representa entidades o instituciones asociadas a deportistas/deportes.
    """
    __tablename__ = "CDRTablaEntidades"

    NIT_ENTIDAD = Column(String(20), primary_key=True)
    RAZON_SOCIAL = Column(String(50))
    TELEFONO = Column(String(20))
    CONTACTO = Column(String(50))
    E_MAIL = Column(String(50))


class Deporte(Base):
    """
    Modelo que mapea a la tabla CDRTablaDeportes.
    Catálogo de deportes.
    """
    __tablename__ = "CDRTablaDeportes"

    ID_DEPORTE = Column(Integer, primary_key=True, autoincrement=True)
    DEPORTE = Column(String(50))


class DeporteDeportista(Base):
    """
    Modelo que mapea a CDRTablaDeportesDeportistas.
    Relaciona deportistas con deportes y entidades.
    """
    __tablename__ = "CDRTablaDeportesDeportistas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ID_DEPORTE = Column(Integer, ForeignKey("CDRTablaDeportes.ID_DEPORTE"))
    IDENTI_DEPORTISTA = Column(String(20), ForeignKey("CDRTablaDeportistas.IDENTI_DEPORTISTA"))
    NIT_ENTIDAD = Column(String(20), ForeignKey("CDRTablaEntidades.NIT_ENTIDAD"))

    deporte = relationship("Deporte")
    deportista = relationship("Deportista")
    entidad = relationship("Entidad")


class Somatotipo(Base):
    """
    Modelo que mapea a la tabla CDRTablaSomatotipo.
    Representa el encabezado de un registro de somatotipo.
    """
    __tablename__ = "CDRTablaSomatotipo"
    id_Somatotipo = Column(Integer, primary_key=True, autoincrement=True)
    FECHA_MEDIDA = Column(Date)
    IDENTI_DEPORTISTA = Column(String(20), ForeignKey("CDRTablaDeportistas.IDENTI_DEPORTISTA"))
    LOGIN_USER = Column(String(60))
    OBSERV = Column(Text)

    deportista = relationship("Deportista")
    detalles = relationship("SomatotipoDetalle", back_populates="somatotipo")

class SomatotipoDetalle(Base):
    """
    Modelo que mapea a la tabla secundaria de detalles de somatotipo.
    Almacena los detalles de las mediciones antropométricas para el cálculo del somatotipo.
    """
    __tablename__ = os.getenv("SOMATOTIPO_DETALLE_TABLE", "CDRTablaSomatotipoDetalle")
    ID = Column(Integer, primary_key=True, autoincrement=True)
    id_Somatotipo = Column(Integer, ForeignKey("CDRTablaSomatotipo.id_Somatotipo"))
    ESTA_USER_CM = Column(DECIMAL(8, 2))
    PESO_kg = Column(DECIMAL(8, 2))
    PLIEGUE_TRICIPITAL = Column(DECIMAL(8, 2))
    PLIEGUE_SUBESCAPULAR = Column(DECIMAL(8, 2))
    PLIEGUE_SUPRAILIACO = Column(DECIMAL(8, 2))
    PLIEGUE_ABDOMINAL = Column(DECIMAL(8, 2))
    PLIEGUE_MUSLO_ANT = Column(DECIMAL(8, 2))
    PLIEGUE_MEDIAL_PIERNA = Column(DECIMAL(8, 2))
    DIAMETRO_BIEPI_MUNECA = Column(DECIMAL(8, 2))
    DIAMETRO_BIEPI_FEMUR = Column(DECIMAL(8, 2))
    DIAMETRO_CODO = Column(DECIMAL(8, 2))
    PERIMETRO_BICED_CONTRAIDO = Column(DECIMAL(8, 2))
    PERIMETRO_PIERNA = Column(DECIMAL(8, 2))
    CIRCUNFERENCIA_CARPO = Column(DECIMAL(8, 2))

    somatotipo = relationship("Somatotipo", back_populates="detalles")

class VistaValoracionCorporal(Base):
    """
    Modelo que mapea a la vista CDRVistaValoracionCorporal.
    """
    __tablename__ = "CDRVistaValoracionCorporal"
    
    # We use id_Somatotipo as primary_key for mapping. 
    # Warning: If view returns multiple rows per ID, SQLAlchemy might deduplicate.
    # Since we lack a unique Detail ID in the view, we assume the view might reduce/calculate 1 row per somatotipo 
    # OR we accept deduplication.
    id_Somatotipo = Column(Integer, primary_key=True)
    FECHA_MEDIDA = Column(Date)
    IDENTI_DEPORTISTA = Column(String(20))
    NOMBRE_DEPORTISTA = Column(String(50))
    # OBSERV and LOGIN_USER were not found in inspection
    
    # Measurements
    ESTA_USER_CM = Column(DECIMAL(12, 6))
    PESO_kg = Column(DECIMAL(12, 6))
    PLIEGUE_TRICIPITAL = Column(DECIMAL(12, 6))
    PLIEGUE_SUBESCAPULAR = Column(DECIMAL(12, 6))
    PLIEGUE_SUPRAILIACO = Column(DECIMAL(12, 6))
    PLIEGUE_ABDOMINAL = Column(DECIMAL(12, 6))
    PLIEGUE_MUSLO_ANT = Column(DECIMAL(12, 6))
    PLIEGUE_MEDIAL_PIERNA = Column(DECIMAL(12, 6))
    
    # ... Add other calculated fields if needed, but for now map the ones used in UI
    DIAMETRO_BIEPI_MUNECA = Column(DECIMAL(12, 6))
    DIAMETRO_BIEPI_FEMUR = Column(DECIMAL(12, 6))
    DIAMETRO_CODO = Column(DECIMAL(12, 6))
    PERIMETRO_BICED_CONTRAIDO = Column(DECIMAL(12, 6))
    PERIMETRO_PIERNA = Column(DECIMAL(12, 6))
    CIRCUNFERENCIA_CARPO = Column(DECIMAL(12, 6))

    # Calculated Fields / Analysis
    EDAD = Column(Integer)
    SEXO_DEPORTISTA = Column(String(1))
    
    # Body Composition (Fat %)
    PorcGrasoJonson = Column(DECIMAL(19, 2))
    PesoGrasoJhonston = Column(DECIMAL(25, 2))
    PorcGrasoFaulker = Column(DECIMAL(14, 2))
    PesoRasoFaulker = Column(DECIMAL(20, 2))
    PorcRasoYuasz = Column(DECIMAL(16, 2))
    PesoRasoYuazs = Column(DECIMAL(22, 2))
    
    # Masses
    PesoOseo = Column(DECIMAL(12, 6)) # DOUBLE in DB, float in python
    PesoResidual = Column(DECIMAL(11, 2))
    Mma = Column(DECIMAL(12, 6)) # Masa Muscular Activa?
    
    # Indices
    IMC = Column(DECIMAL(12, 6))
    EstadoIMC = Column(String(50))
    Complexion = Column(DECIMAL(15, 2))
    TipoComplexion = Column(String(10))
    
    # Somatotype components
    Endomorfismo = Column(DECIMAL(12, 6))
    EscalaEndomorfismo = Column(Text)
    Mesomorfismo = Column(DECIMAL(15, 2))
    EscalaMesomorfismo = Column(Text)
    Ectomorfismo = Column(DECIMAL(12, 6))
    EscalaEctomorfismo = Column(Text)
    X = Column(DECIMAL(12, 6))
    Y = Column(DECIMAL(12, 6))


class Auditoria(Base):
    """
    Modelo que mapea a la tabla CDRTablaAuditoria.
    Registra todas las acciones de auditoría del sistema.
    """
    __tablename__ = "CDRTablaAuditoria"
    
    ID_AUDIT = Column(Integer, primary_key=True, autoincrement=True)
    OCCURRED_AT_UTC = Column(DateTime(6), nullable=False)
    ACTOR_USER_ID = Column(Integer, nullable=True)
    ACTOR_LOGIN = Column(String(60), nullable=True)
    ACTION_CODE = Column(String(80), nullable=False)
    RESOURCE_TYPE = Column(String(80), nullable=True)
    RESOURCE_ID = Column(String(120), nullable=True)
    EVENT_RESULT = Column(String(20), nullable=False)
    HTTP_METHOD = Column(String(10), nullable=True)
    ENDPOINT = Column(String(255), nullable=True)
    STATUS_CODE = Column(Integer, nullable=True)
    CLIENT_IP = Column(String(45), nullable=True)
    USER_AGENT = Column(String(500), nullable=True)
    CORRELATION_ID = Column(String(36), nullable=True)
    REQUEST_JSON = Column(Text, nullable=True)
    RESPONSE_JSON = Column(Text, nullable=True)
    ERROR_MESSAGE = Column(Text, nullable=True)
