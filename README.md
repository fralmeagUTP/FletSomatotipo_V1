# Somatocarta

**Versión:** v1.2.1
**Estado:** 95% funcional; Android y Flet Web comparten frontend responsive, E2E crítico y PDFs optimizados

Aplicación Flet + FastAPI para gestión de deportistas, valoración corporal antropométrica, análisis de composición corporal, somatotipo (Heath-Carter), análisis longitudinal e informes PDF.

Somatocarta forma parte de **SINVADE — Sistema Integral de Valoración Deportiva**.

## Funcionalidades principales

- **Autenticación JWT** con auditoría de login.
- **Dashboard** con métricas operativas y accesos rápidos mediante iconos vectoriales.
- **CRUD de deportistas** con fotografía, catálogos y validaciones.
- **CRUD de entidades** deportivas (ligas, clubes, instituciones).
- **CRUD de deportes** con catálogo.
- **CRUD de asignaciones** deportista-entidad-deporte.
- **Valoración corporal** con 14 campos antropométricos y múltiples tomas de medición.
- **Análisis individual** con Yuhasz como método principal, Faulkner como comparación, IMC, complexión, somatotipo y somatocarta.
- **Análisis longitudinal** con gráficos de tendencia, somatocarta con trayectoria y comparación temporal.
- **Informes PDF** individuales y longitudinales construidos internamente, con Pillow para optimizar imágenes.
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
| PDF | Generación manual PDF 1.4 + Pillow para imágenes |
| Testing | pytest (206 tests y 7 subpruebas) |
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
ACCESS_TOKEN_EXPIRE_MINUTES=30
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

## Ejecución Web con Flet

La versión web reutiliza la misma función `main`, las mismas vistas, el tema y `ApiClient` de Android. Requiere `flet-web==0.85.3`, incluido en `requirements.txt`.

Configurar en `.env`:

```text
API_URL=http://127.0.0.1:8085
WEB_HOST=0.0.0.0
WEB_PORT=8550
WEB_ALLOWED_ORIGINS=http://localhost:8550,http://127.0.0.1:8550
```

Iniciar FastAPI y, en otra terminal, Flet Web:

```powershell
.\start_backend.bat
.\start_web.bat
```

Abrir `http://localhost:8550`. También puede ejecutarse manualmente:

```powershell
$env:APP_RUNTIME="web"
.\.venv\Scripts\python.exe web_main.py
```

Para un servidor sin interfaz gráfica se expone una fábrica ASGI:

```powershell
.\.venv\Scripts\python.exe -m uvicorn web_main:create_web_app --factory --host 0.0.0.0 --port 8550
```

La guía de publicación, proxy HTTPS y variables está en `docs/flet_web_deployment.md`.

Para hosting compartido sin VPS, la arquitectura recomendada conserva FastAPI en cPanel y publica Flet Web en Render bajo `https://somatocarta.nyquist.app`. Consulte `docs/flet_web_no_vps.md`.

## Estructura del proyecto

```text
SomatoCarta_V1.0/
├── main.py                     # Entrada del frontend Flet
├── web_main.py                 # Entrada y fábrica ASGI de Flet Web
├── app_config.py               # Configuración compartida
├── passenger_wsgi.py           # Despliegue cPanel/Passenger
├── start_backend.bat           # Script de inicio del backend
├── start_frontend.bat          # Script de inicio del frontend
├── start_web.bat               # Script de inicio de Flet Web
├── requirements.txt            # Dependencias completas
├── requirements-web.txt        # Dependencias mínimas de Flet Web
├── render.yaml                 # Despliegue administrado sin VPS
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
│   │   ├── runtime.py          # Descargas diferenciadas Web/nativo
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
│       ├── services/           # Lógica de negocio y PDFs
│       └── domain/             # Calculadora antropométrica de referencia
├── tests/                      # 206 tests en 30 archivos
├── scripts/                    # Migraciones y utilidades
├── assets/                     # Imágenes, íconos, logotipos
└── docs/                       # Documentación
    ├── specs/
    │   ├── somatocarta_spec.md # Especificación Spec Kit
    │   └── flet_web/           # Especificación Web
    ├── architecture.md         # Arquitectura técnica
    ├── modules.md              # Módulos funcionales
    ├── formulas_somatotipo.md  # Fórmulas y cálculos
    ├── user_guide.md           # Guía de usuario
    ├── testing_plan.md         # Plan de pruebas
    ├── qa_checklist.md         # Checklist QA
    ├── estado_funcional.md     # Porcentaje y pendientes vigentes
    ├── integridad_referencial.md
    ├── documentation_governance.md
    ├── changelog_documentation.md
    ├── publicacion.md          # Checklist de publicación
    ├── uploads.md              # Política de uploads
    ├── flet_web_deployment.md  # Despliegue Web
    ├── flet_web_qa_checklist.md
    └── qa/                     # Informes históricos
```

## Módulos

| Módulo | Descripción |
|--------|-------------|
| Login | Autenticación JWT con auditoría |
| Dashboard | Métricas operativas, estado del sistema y accesos rápidos |
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
| Pruebas / QA | 206 pruebas y 7 subpruebas unitarias, de integración y E2E (`tests/`) |

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Resultado actual: **206 tests y 7 subpruebas pasando**.

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
| `docs/integridad_referencial.md` | Política `RESTRICT`, duplicados y migración MySQL |
| `docs/estado_funcional.md` | Porcentaje funcional, evidencia y pendientes vigentes |
| `docs/documentation_governance.md` | Inventario, reglas y fuentes de verdad documentales |
| `docs/changelog_documentation.md` | Historial de cambios documentales |
| `docs/flet_web_deployment.md` | Ejecución y despliegue de Flet Web |
| `docs/flet_web_no_vps.md` | Despliegue recomendado manteniendo el backend en cPanel |
| `docs/flet_web_qa_checklist.md` | Checklist responsive y funcional de Flet Web |
| `docs/specs/flet_web/` | Especificación, plan y tareas de la versión web |

## Contexto institucional

Somatocarta es desarrollada en el marco de:

- **Grupo de Investigación Nyquist**
- **Grupo de Investigación y Desarrollo en Cultura de la Salud**
- **Laboratorio de Movimiento Humano**
- **Programa de Ciencias del Deporte** — Facultad de Ciencias de la Salud
- **Programa de Ingeniería de Sistemas y Computación** — Facultad de Ingenierías
- **Universidad Tecnológica de Pereira**

## Estado actual

- **Versión:** v1.2.1
- **Tests:** 206 y 7 subpruebas pasando
- **Estabilidad:** 95% funcional; flujos principales, Web inicial y E2E crítico operativos
- **Última evaluación QA:** 22 de junio de 2026
- **MySQL:** 76 valoraciones verificadas, 0 diferencias de cálculo

## Advertencias importantes

1. **Cálculos antropométricos:** La migración `004` está aplicada en la base activa; 76 valoraciones coinciden con la calculadora Python. Las bases adicionales también deben migrarse y el protocolo requiere aprobación metodológica del equipo de ciencias del deporte.
2. **Seguridad:** Las contraseñas están almacenadas en texto plano por compatibilidad con la base de datos heredada. Se recomienda migrar a hash seguro.
3. **Integridad referencial:** La API y la base activa bloquean la eliminación de deportistas, entidades o deportes con dependencias. Las bases adicionales deben aplicar las migraciones `002` y `003`.
4. **Duplicados:** La API y la migración MySQL impiden deportes y asignaciones duplicadas.
5. **Flet Web:** Antes de publicar, configure `WEB_ALLOWED_ORIGINS`, HTTPS y un proxy con soporte WebSocket.

## Notas de mantenimiento

- No guardar secretos en Git; usar `.env`.
- No usar `requests` directamente en vistas; usar `src/frontend/api_client.py`.
- Mantener routers backend delgados; mover lógica a `src/backend/services/`.
- El icono de build usa `assets/icon.png` y la ventana Windows usa `assets/icon.ico`.
- Antes de publicar, revisar archivos no relacionados como backups `.zip` e imágenes en `src/backend/static/uploads/`.
