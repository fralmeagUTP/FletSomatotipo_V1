# Somatocarta

**Versión:** v1.1.7
**Estado:** Funcional con hallazgos QA pendientes

Aplicación Flet + FastAPI para gestión de deportistas, valoración corporal antropométrica, análisis de composición corporal, somatotipo (Heath-Carter), análisis longitudinal e informes PDF.

Somatocarta forma parte de **SINVADE — Sistema Integral de Valoración Deportiva**.

## Funcionalidades principales

- **Autenticación JWT** con auditoría de login.
- **Dashboard** con métricas operativas y actividad reciente.
- **CRUD de deportistas** con fotografía, catálogos y validaciones.
- **CRUD de entidades** deportivas (ligas, clubes, instituciones).
- **CRUD de deportes** con catálogo.
- **CRUD de asignaciones** deportista-entidad-deporte.
- **Valoración corporal** con 14 campos antropométricos y múltiples tomas de medición.
- **Análisis individual** con composición corporal (3 métodos de grasa), IMC, complexión, somatotipo y somatocarta.
- **Análisis longitudinal** con gráficos de tendencia, somatocarta con trayectoria y comparación temporal.
- **Informes PDF** individuales y longitudinales generados sin dependencias externas.
- **Sistema de auditoría** con registro en base de datos y archivo log.
- **Diseño responsive** para escritorio, tablet y móvil (incluye Android).

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Frontend | Flet (Python, multiplataforma) |
| Backend | FastAPI + Uvicorn |
| ORM | SQLAlchemy |
| Base de datos | MySQL (pymysql) |
| Validación | Pydantic + email-validator |
| Autenticación | JWT (python-jose) |
| PDF | Generación manual PDF 1.4 (sin dependencias) |
| Testing | pytest (162 tests) |
| Despliegue | cPanel/Passenger (a2wsgi) |

## Instalación y ejecución

### 1. Clonar el repositorio

```powershell
git clone <url-del-repositorio>
cd SomatoCarta_V1.0
```

### 2. Crear entorno virtual e instalar dependencias

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copiar `.env.example` a `.env` y ajustar:

```text
API_URL=http://127.0.0.1:8085
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8085
DB_HOST=localhost
DB_USER=usuario
DB_PORT=3306
DB_PASSWORD=contrasena
DB_NAME=somatocarta
SECRET_KEY=cambia-este-valor
```

### 4. Ejecutar backend

```powershell
.\start_backend.bat
```

O manualmente:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8085
```

### 5. Ejecutar frontend (otra terminal)

```powershell
.\start_frontend.bat
```

O manualmente:

```powershell
.\.venv\Scripts\python.exe main.py
```

## Estructura del proyecto

```text
SomatoCarta_V1.0/
├── main.py                     # Entrada del frontend Flet
├── app_config.py               # Configuración compartida
├── passenger_wsgi.py           # Despliegue cPanel/Passenger
├── start_backend.bat           # Script de inicio del backend
├── start_frontend.bat          # Script de inicio del frontend
├── requirements.txt            # Dependencias completas
├── requirements-apk.txt        # Dependencias para APK Android
├── views/                      # Pantallas Flet (9 vistas)
│   ├── dashboard.py
│   ├── deportistas.py
│   ├── valoracion.py
│   ├── historial.py
│   ├── analisis_longitudinal.py
│   ├── entidades.py
│   ├── deportes.py
│   ├── asignaciones.py
│   └── acerca.py
├── src/
│   ├── anthropometry.py        # Reglas de validación antropométrica
│   ├── frontend/               # Cliente API, componentes, navegación
│   │   ├── api_client.py
│   │   ├── app_shell.py
│   │   ├── navigation.py
│   │   ├── components.py
│   │   ├── theme.py
│   │   ├── form_helpers.py
│   │   ├── table_builders.py
│   │   ├── assets.py
│   │   ├── somatocarta.py
│   │   ├── composition_analysis.py
│   │   ├── longitudinal_analysis.py
│   │   ├── interpretation.py
│   │   └── formatters.py
│   └── backend/                # API REST
│       ├── main.py             # Entrada FastAPI
│       ├── models.py           # Modelos SQLAlchemy (11 modelos)
│       ├── database.py         # Conexión MySQL
│       ├── auth_utils.py       # JWT y autenticación
│       ├── audit.py            # Sistema de auditoría
│       ├── routers/            # 7 routers API
│       ├── schemas/            # Schemas Pydantic
│       └── services/           # Lógica de negocio (6 servicios)
├── tests/                      # 162 tests en 24 archivos
├── scripts/                    # Migraciones y utilidades
├── assets/                     # Imágenes, íconos, logotipos
└── docs/                       # Documentación
    ├── specs/
    │   └── somatocarta_spec.md # Especificación Spec Kit
    ├── architecture.md         # Arquitectura técnica
    ├── modules.md              # Módulos funcionales
    ├── formulas_somatotipo.md  # Fórmulas y cálculos
    ├── user_guide.md           # Guía de usuario
    ├── testing_plan.md         # Plan de pruebas
    ├── qa_checklist.md         # Checklist QA
    ├── documentation_inventory.md
    ├── deprecated_docs_report.md
    ├── changelog_documentation.md
    ├── publicacion.md          # Checklist de publicación
    └── uploads.md              # Política de uploads
```

## Módulos

| Módulo | Descripción |
|--------|-------------|
| Login | Autenticación JWT con auditoría |
| Dashboard | Métricas operativas y actividad reciente |
| Deportistas | CRUD con fotografía y catálogos |
| Entidades | CRUD de entidades deportivas |
| Deportes | CRUD de catálogo de deportes |
| Asignaciones | Relación deportista-entidad-deporte |
| Valoración Corporal | Captura de 14 campos antropométricos |
| Análisis Individual | Composición corporal, IMC, somatotipo, somatocarta |
| Análisis Longitudinal | Evolución temporal con gráficos |
| Informes PDF | Individual y longitudinal |
| Acerca | Información institucional |
| Gestión de usuarios | *(Pendiente)* Actualmente en BD sin interfaz |
| Menú principal | Navegación responsive entre módulos |
| Pruebas / QA | 162 pruebas unitarias y de integración (`tests/`) |

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Resultado actual: **162 tests pasando**.

Preflight de publicación:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\preflight_publicacion.ps1
```

## Documentación

| Documento | Propósito |
|-----------|-----------|
| `docs/specs/somatocarta_spec.md` | Especificación completa tipo Spec Kit |
| `docs/architecture.md` | Arquitectura técnica |
| `docs/modules.md` | Descripción funcional de módulos |
| `docs/formulas_somatotipo.md` | Fórmulas y cálculos antropométricos |
| `docs/user_guide.md` | Guía de usuario |
| `docs/testing_plan.md` | Plan de pruebas |
| `docs/qa_checklist.md` | Checklist de evaluación QA |
| `docs/publicacion.md` | Checklist de publicación |
| `docs/uploads.md` | Política de archivos subidos |
| `docs/documentation_inventory.md` | Inventario documental |
| `docs/deprecated_docs_report.md` | Documentos obsoletos |
| `docs/changelog_documentation.md` | Historial de cambios documentales |

## Contexto institucional

Somatocarta es desarrollada en el marco de:

- **Grupo de Investigación Nyquist**
- **Grupo de Investigación y Desarrollo en Cultura de la Salud**
- **Laboratorio de Movimiento Humano**
- **Programa de Ciencias del Deporte** — Facultad de Ciencias de la Salud
- **Programa de Ingeniería de Sistemas y Computación** — Facultad de Ingenierías
- **Universidad Tecnológica de Pereira**

## Estado actual

- **Versión:** v1.1.7
- **Tests:** 162 pasando
- **Estabilidad:** Funcional con hallazgos QA documentados
- **Última evaluación QA:** 15 de junio de 2026

## Advertencias importantes

1. **Cálculos clínicos:** Los indicadores de somatotipo se calculan en la vista SQL `CDRVistaValoracionCorporal`. Se han detectado valores anómalos en mesomorfismo (negativo) y peso óseo (irrealmente bajo). Pendiente de validación clínica.
2. **Seguridad:** Las contraseñas están almacenadas en texto plano por compatibilidad con la base de datos heredada. Se recomienda migrar a hash seguro.
3. **Integridad referencial:** Las operaciones de eliminación no validan dependencias. Se pueden eliminar entidades, deportes o deportistas con datos asociados.
4. **Duplicados:** El sistema no previene la creación de deportes o asignaciones duplicadas.

## Notas de mantenimiento

- No guardar secretos en Git; usar `.env`.
- No usar `requests` directamente en vistas; usar `src/frontend/api_client.py`.
- Mantener routers backend delgados; mover lógica a `src/backend/services/`.
- El icono de build usa `assets/icon.png` y la ventana Windows usa `assets/icon.ico`.
- Antes de publicar, revisar archivos no relacionados como backups `.zip` e imágenes en `src/backend/static/uploads/`.
