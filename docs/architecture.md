# Arquitectura de Somatocarta v1.2.1

**Fecha de actualización:** 21 de junio de 2026

---

## Objetivo

Somatocarta es una aplicación Flet + FastAPI para gestionar deportistas, registrar valoraciones antropométricas, consultar historial de somatotipo, generar análisis individuales y longitudinales, y producir informes PDF. Forma parte de SINVADE (Sistema Integral de Valoración Deportiva).

## Estructura principal

```text
main.py                         # Entrada del frontend Flet (v1.2.1)
app_config.py                   # Configuración compartida del frontend
views/                          # Pantallas Flet (9 vistas)
  dashboard.py                  # Dashboard con métricas y actividad reciente
  deportistas.py                # CRUD de deportistas
  valoracion.py                 # Captura de valoración corporal
  historial.py                  # Análisis individual de valoración
  analisis_longitudinal.py      # Análisis longitudinal
  entidades.py                  # CRUD de entidades
  deportes.py                   # CRUD de deportes
  asignaciones.py               # CRUD de asignaciones
  acerca.py                     # Información del proyecto
src/frontend/                   # Cliente API, navegación, tema y helpers UI
  api_client.py                 # Cliente HTTP central
  app_shell.py                  # Shell de la app (sidebar + menú móvil)
  navigation.py                 # Navegación centralizada con Lock
  theme.py                      # Colores, sombras y constantes visuales
  components.py                 # Componentes UI reutilizables
  form_helpers.py               # Construcción de payloads
  table_builders.py             # Filas y agrupación de tablas
  assets.py                     # Rutas de imágenes
  somatocarta.py                # Calibración y render de somatocarta
  composition_analysis.py       # Análisis de composición corporal
  longitudinal_analysis.py      # Análisis temporal
  interpretation.py             # Notas metodológicas
  formatters.py                 # Formateo de valores
src/backend/main.py             # Entrada FastAPI (7 routers)
src/backend/routers/            # Capa HTTP/API
  auth.py                       # Autenticación (login, JWT)
  deportistas.py                # CRUD de deportistas
  entidades_deportes.py         # CRUD de entidades, deportes y asignaciones
  somatotipo.py                 # Valoraciones, historial, PDFs
  catalogos.py                  # Catálogos (tipos doc, estratos, niveles)
  files.py                      # Carga de imágenes
  dashboard.py                  # Métricas de dashboard
src/backend/schemas/            # Modelos Pydantic
  deportistas.py                # Schema de deportistas
  entidades_deportes.py         # Schemas de entidades, deportes, asignaciones
  somatotipo.py                 # Schema de valoración (14 campos + rangos)
src/backend/services/           # Reglas de aplicación y transacciones DB
  deportistas_service.py        # CRUD de deportistas
  entidades_deportes_service.py # CRUD de entidades, deportes, asignaciones
  somatotipo_service.py         # Valoraciones, PDFs, historial
  dashboard_service.py          # Métricas de dashboard
  view_contract_service.py      # Validación de vista SQL
  pdf_service.py                # Generación manual y optimizada de PDFs
src/backend/domain/
  anthropometry_calculator.py   # Calculadora clínica pura de referencia
src/backend/models.py           # Modelos SQLAlchemy (11 modelos)
src/backend/database.py         # Configuración de conexión MySQL
src/backend/auth_utils.py       # JWT, verificación de contraseña, get_current_user
src/backend/audit.py            # Sistema de auditoría (DB + archivo log)
src/anthropometry.py            # Reglas de validación de mediciones
tests/                          # 183 pruebas en 27 archivos
scripts/                        # Migraciones, inspección y verificación MySQL
```

## Flujo frontend

1. `main.py` muestra login.
2. `ApiClient.login()` autentica contra `/auth/login`.
3. La sesión guarda `access_token`, `username`, `login_user` y `user_id`.
4. `navigation.py` redirige al dashboard.
5. `app_shell.py` alterna dinámicamente sidebar (desktop) y menú hamburguesa (móvil) al cambiar el ancho, con búsqueda global.
6. Las vistas usan `ApiClient` para consumir backend.
7. Componentes reutilizables en `components.py`, `theme.py`, `form_helpers.py`, `table_builders.py`.

## Flujo backend

1. `src/backend/main.py` registra 7 routers y monta archivos estáticos.
2. Los routers validan request/response con schemas Pydantic.
3. Los routers delegan operaciones a servicios.
4. Los servicios usan modelos SQLAlchemy y controlan `commit()` / `rollback()`.
5. Las rutas privadas usan `Depends(get_current_user)`.
6. `audit.py` registra operaciones en `CDRTablaAuditoria` y `audit.log`.

## Endpoints principales

### Autenticación
- `POST /auth/login` — Autenticación

### Dashboard
- `GET /dashboard/summary` — Métricas operativas

### Deportistas
- `GET /deportistas/` — Listado paginado
- `GET /deportistas/{identi}` — Detalle
- `POST /deportistas/` — Crear
- `PUT /deportistas/{identi}` — Actualizar
- `DELETE /deportistas/{identi}` — Eliminar

### Entidades
- `GET /entidades/` — Listado paginado
- `POST /entidades/` — Crear
- `PUT /entidades/{nit}` — Actualizar
- `DELETE /entidades/{nit}` — Eliminar

### Deportes
- `GET /deportes/` — Listado paginado
- `POST /deportes/` — Crear
- `PUT /deportes/{deporte_id}` — Actualizar
- `DELETE /deportes/{deporte_id}` — Eliminar

### Asignaciones
- `GET /asignaciones/` — Listado paginado
- `POST /asignaciones/` — Crear
- `PUT /asignaciones/{id}` — Actualizar
- `DELETE /asignaciones/{id}` — Eliminar

### Catálogos
- `GET /catalogos/tipos_documento`
- `GET /catalogos/estratos`
- `GET /catalogos/niveles_educativos`

### Valoraciones y Somatotipo
- `POST /somatotipo/` — Crear valoración con detalles
- `GET /somatotipo/deportista/{identi}` — Historial desde tablas base
- `GET /somatotipo/vista/deportista/{identi}` — Historial desde vista SQL
- `GET /somatotipo/editable/deportista/{identi}` — Valoraciones editables (listado)
- `GET /somatotipo/editable/{id}` — Valoración editable (detalle)
- `POST /somatotipo/{id}/detalle` — Agregar toma adicional
- `PUT /somatotipo/detalle/{id}` — Actualizar medición
- `DELETE /somatotipo/detalle/{id}` — Eliminar medición
- `DELETE /somatotipo/{id}` — Eliminar valoración completa
- `GET /somatotipo/{id}/pdf` — PDF individual
- `GET /somatotipo/vista/deportista/{identi}/longitudinal/pdf` — PDF longitudinal
- `GET /somatotipo/vista/contrato` — Validación de columnas de vista SQL

### Archivos
- `POST /files/upload` — Carga de imagen (JPG/PNG, máx 5 MB)

### Salud
- `GET /` — Health check básico
- `GET /health` — Verificación de conexión a base de datos

## Paginación

Los listados devuelven:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 50
}
```

## Cálculos de somatotipo

La base de datos calcula los indicadores mediante `CDRVistaValoracionCorporal` y sus vistas dependientes. `src/backend/domain/anthropometry_calculator.py` replica las ecuaciones como referencia pura y testeable. La documentación metodológica está en `docs/formulas_somatotipo.md`.

## Sistema de auditoría

`src/backend/audit.py` registra operaciones en:
- Tabla `CDRTablaAuditoria` (MySQL).
- Archivo `audit.log` (texto plano con rotación).

Operaciones auditadas: login (éxito/fallo), CRUD de deportistas, operaciones de somatotipo (crear/actualizar/eliminar encabezado y detalles), descargas de PDF.

## Generación de PDFs

`src/backend/services/pdf_service.py` genera PDFs manualmente usando primitivas PDF 1.4. Pillow acelera la conversión y reducción de imágenes; existe un decodificador PNG interno como fallback. Incluye:
- Decodificador PNG interno con filtro Paeth.
- Render de somatocarta calibrada.
- Gráficos de línea longitudinales.
- Gráficos de distribución de masas.
- Documentos multi-página con xref/trailer.

## Pruebas

183 tests y 3 subpruebas en 27 archivos. Comando:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

## Decisiones relevantes

- La URL del backend se centraliza en `app_config.py`.
- Las rutas privadas están protegidas por token JWT.
- El frontend no usa `requests` directamente fuera de `ApiClient`.
- Los routers no contienen lógica de transacción; esa responsabilidad está en servicios.
- Los schemas Pydantic viven fuera de routers para mantener separación de capas.
- Los cálculos clínicos viven en la vista SQL.
- Las relaciones críticas usan política `RESTRICT`; la API responde HTTP 409 cuando existen dependencias.
- Las contraseñas están en texto plano por compatibilidad con base de datos heredada.
- El despliegue en cPanel usa `passenger_wsgi.py` con `a2wsgi`.

## Pendientes recomendados

- Validar clínicamente la definición SQL de `CDRVistaValoracionCorporal`.
- Aplicar las migraciones `002`, `003` y `004` únicamente en bases adicionales o restauradas; la base activa ya está migrada y verificada.
- Migrar contraseñas a hash seguro.
- Añadir control de roles y permisos y definir CORS por ambiente.
- Completar pruebas E2E visuales responsive.
- Añadir migraciones de base de datos con Alembic.
- Limpiar binarios/backups antes de publicar.

El estado funcional ponderado y su evidencia se mantienen en `docs/estado_funcional.md`.
