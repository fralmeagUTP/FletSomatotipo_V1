# Sistema de Auditoría - SomatoCarta

## 1. IMPLEMENTACIÓN DE AUDITORÍA

### A. Configuración de Logging Estructurado

Crear archivo `src/backend/audit.py`:

```python
import logging
import json
from datetime import datetime
from functools import wraps
from typing import Optional, Dict, Any

# Configurar logger
logger = logging.getLogger('somatocarta')
logger.setLevel(logging.INFO)

# Handler para archivo
file_handler = logging.FileHandler('audit.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# Formato
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

def log_action(
    action: str,
    user: Optional[str] = None,
    resource: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
):
    """Registra una acción de usuario"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'action': action,
        'user': user,
        'resource': resource,
        'resource_id': resource_id,
        'details': details,
        'ip_address': ip_address
    }
    logger.info(json.dumps(log_entry, ensure_ascii=False))

def audit_endpoint(action: str, resource: str):
    """Decorator para auditar endpoints automáticamente"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener usuario del contexto
            user = None
            try:
                from fastapi import Request
                request = kwargs.get('request')
                if request:
                    user = request.state.user
            except:
                pass
            
            # Ejecutar la función
            result = func(*args, **kwargs)
            
            # Registrar la acción
            log_action(
                action=action,
                user=user,
                resource=resource,
                details={'status': 'success'}
            )
            
            return result
        return wrapper
    return decorator
```

### B. Tabla de Auditoría en Base de Datos

```sql
CREATE TABLE audit_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    username VARCHAR(60),
    action VARCHAR(50) NOT NULL,
    resource VARCHAR(50),
    resource_id VARCHAR(50),
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_timestamp (timestamp),
    INDEX idx_resource (resource, resource_id)
);

-- Tipos de acciones
-- LOGIN_SUCCESS, LOGIN_FAILED, LOGOUT
-- CREATE_DEPORTISTA, UPDATE_DEPORTISTA, DELETE_DEPORTISTA
-- CREATE_VALORACION, UPDATE_VALORACION, DELETE_VALORACION
-- GENERATE_PDF, VIEW_REPORT
-- CREATE_USER, UPDATE_USER, DELETE_USER
```

### C. Integración en Routers

Ejemplo para `src/backend/routers/auth.py`:

```python
from ..audit import log_action

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.LOGIN_USER == request.username).first()
    
    if not user or user.PSW_USER != request.password:
        log_action(
            action='LOGIN_FAILED',
            user=request.username,
            details={'reason': 'invalid_credentials'}
        )
        raise HTTPException(401, "Credenciales inválidas")
    
    log_action(
        action='LOGIN_SUCCESS',
        user=user.LOGIN_USER,
        details={'user_id': user.ID_USER}
    )
    
    # ... resto del código
```

Ejemplo para `src/backend/routers/deportistas.py`:

```python
from ..audit import log_action, audit_endpoint

@router.post("/", response_model=DeportistaResponse)
def crear_deportista(d: DeportistaCreate, db: Session = Depends(get_db)):
    result = deportistas_service.create_deportista(db, d.model_dump())
    
    log_action(
        action='CREATE_DEPORTISTA',
        resource='deportistas',
        resource_id=result.get('IDENTI_DEPORTISTA'),
        details={'nombre': d.NOMBRE_DEPORTISTA}
    )
    
    return result

@router.delete("/{identi}")
def eliminar_deportista(identi: str, db: Session = Depends(get_db)):
    # Obtener datos antes de eliminar
    deportista = deportistas_service.get_deportista_or_404(db, identi)
    
    result = deportistas_service.delete_deportista(db, identi)
    
    log_action(
        action='DELETE_DEPORTISTA',
        resource='deportistas',
        resource_id=identi,
        details={
            'nombre': deportista.NOMBRE_DEPORTISTA,
            'deleted_at': datetime.utcnow().isoformat()
        }
    )
    
    return result
```

### D. Middleware de Logging para FastAPI

Crear `src/backend/middleware.py`:

```python
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger('somatocarta.requests')

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Procesar request
        response = await call_next(request)
        
        # Calcular duración
        duration = time.time() - start_time
        
        # Obtener usuario si está autenticado
        user = getattr(request.state, 'user', None)
        
        # Log solo para endpoints importantes
        if request.url.path not in ['/health', '/', '/docs', '/openapi.json']:
            logger.info({
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'user': user,
                'client_ip': request.client.host if request.client else None
            })
        
        return response

# En main.py:
from .middleware import RequestLoggingMiddleware
app.add_middleware(RequestLoggingMiddleware)
```

### E. Rotación de Logs

Configurar `logging.conf`:

```ini
[loggers]
keys=root,somatocarta

[handlers]
keys=consoleHandler,fileHandler,rotatingFileHandler

[formatters]
keys=standard

[logger_root]
level=WARNING
handlers=consoleHandler

[logger_somatocarta]
level=INFO
handlers=rotatingFileHandler
qualname=somatocarta
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=WARNING
formatter=standard
args=(sys.stdout,)

[handler_rotatingFileHandler]
class=handlers.RotatingFileHandler
level=INFO
formatter=standard
args=('audit.log', 'a', 10485760, 5)

[formatter_standard]
format=%(asctime)s | %(levelname)s | %(name)s | %(message)s
```

---

## 2. RESUMEN DE LO REALIZADO

### Funcionalidades Implementadas

#### A. Módulo de Valoración Corporal
- ✅ Wizard de 4 pasos (Datos Básicos → Pliegues → Diámetros → Revisar)
- ✅ Validación en tiempo real de campos numéricos
- ✅ Auto-limpieza del formulario después de agregar medición
- ✅ Botón "Duplicar anterior" para mediciones similares
- ✅ Tarjetas detalladas para cada medición (no tabla compacta)
- ✅ Confirmación antes de eliminar mediciones
- ✅ Indicadores visuales de campos obligatorios (*)
- ✅ Fecha por defecto = fecha del sistema, editable con DatePicker

#### B. Información del Deportista
- ✅ Tarjeta visual con foto, ID, nombre, edad, email, dirección, ciudad, departamento
- ✅ Implementado en Valoración y Asignaciones
- ✅ Diseño responsive (foto + información en fila)

#### C. Dashboard Mejorado
- ✅ Header con título y subtítulo
- ✅ Información de usuario activo (👤 nombre)
- ✅ Botón de Cerrar Sesión funcional
- ✅ Tarjetas de métricas (Deportistas, Valoraciones, Vista SQL)
- ✅ Sección "Módulos del sistema"

#### D. Diseño Responsive
- ✅ Historial Corporal: layout master-detail adaptativo
- ✅ Dashboard: grid responsive (2/3/6 columnas según pantalla)
- ✅ Formularios: breakpoints xs/sm/md/lg
- ✅ Tablas: scroll horizontal en móvil

#### E. Correcciones de Bugs
- ✅ PDF: codificación cp1252 con errors="replace"
- ✅ Navegación: uso de page.clean() en lugar de page.controls.clear()
- ✅ Logout: variable de módulo en lugar de page.session para callback
- ✅ Modelo SomatotipoDetalle: tabla correcta CDRTablaSomatotipoDetalle
- ✅ Flet: reinstalación de versión 0.28.3

#### F. Pruebas
- ✅ 138 pruebas pasando
- ✅ Tests E2E de creación de valoraciones
- ✅ Verificación de datos en base de datos

---

## 3. DASHBOARD ABIERTO

✅ **El dashboard está abierto y visible**

- **Usuario:** Administrador del sistema (admin)
- **Contraseña:** CDR2026
- **Estado:** Sesión activa
- **Métricas:**
  - Deportistas: 36
  - Valoraciones: 42
  - Vista SQL: OK (41/41 columnas)

La ventana de Somatocarta debería estar visible en tu pantalla mostrando el dashboard con:
- Header: "Dashboard" / "Resumen operativo"
- Esquina superior derecha: 👤 Administrador del sistema + botón 🚪
- 3 tarjetas de métricas
- 6 módulos del sistema (Deportistas, Valoración, Historial, Deportes, Asignaciones, Entidades)

---

## 4. PRÓXIMOS PASOS RECOMENDADOS

### Prioridad Alta
1. **Implementar logging básico** (ver sección 1.A)
2. **Log de autenticación** (login success/failed)
3. **Log de operaciones CRUD** (create/update/delete)

### Prioridad Media
4. **Tabla de auditoría en BD** (ver sección 1.B)
5. **Middleware de logging** (ver sección 1.D)
6. **Rotación de logs** (ver sección 1.E)

### Prioridad Baja
7. **Dashboard de monitoreo**
8. **Alertas de seguridad**
9. **Backup de logs**

---

## 5. CÓMO USAR EL SISTEMA DE AUDITORÍA

### Instalación

1. Crear archivo `src/backend/audit.py` con el código de la sección 1.A
2. Agregar tabla `audit_log` en la base de datos (sección 1.B)
3. Modificar routers para usar `log_action()` (ejemplos en sección 1.C)
4. Agregar middleware en `src/backend/main.py` (sección 1.D)
5. Configurar rotación con `logging.conf` (sección 1.E)

### Consulta de Logs

```python
# Ver logs en tiempo real
tail -f audit.log

# Buscar acciones de un usuario
grep '"user": "admin"' audit.log

# Buscar eliminaciones
grep '"action": "DELETE_' audit.log

# Buscar intentos de login fallidos
grep '"action": "LOGIN_FAILED"' audit.log
```

### Consulta en Base de Datos

```sql
-- Ver todas las acciones de hoy
SELECT * FROM audit_log 
WHERE DATE(timestamp) = CURDATE()
ORDER BY timestamp DESC;

-- Ver acciones de un usuario específico
SELECT * FROM audit_log 
WHERE username = 'admin'
ORDER BY timestamp DESC;

-- Ver eliminaciones
SELECT * FROM audit_log 
WHERE action LIKE 'DELETE_%'
ORDER BY timestamp DESC;

-- Resumen de acciones por tipo
SELECT action, COUNT(*) as count
FROM audit_log
GROUP BY action
ORDER BY count DESC;
```

---

**Documento generado:** 11 de junio de 2026
**Versión:** 1.0
**Autor:** Sistema de Desarrollo SomatoCarta
