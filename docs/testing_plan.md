# Plan de pruebas — Somatocarta v1.2.5

**Fecha:** 22 de junio de 2026

---

## 1. Estrategia de pruebas

### 1.1 Niveles de prueba

| Nivel | Descripción | Herramienta |
|-------|-------------|-------------|
| Unitarias | Funciones puras y helpers | pytest |
| Componentes | Componentes UI y módulos frontend | pytest + mocks |
| Integración | Servicios backend con SQLite temporal | pytest + SQLAlchemy |
| API | Endpoints HTTP con autenticación | pytest + requests |
| Funcionales | Flujos completos de usuario | Pruebas manuales + API |
| E2E | Recorrido visual completo | Pruebas manuales |

### 1.2 Ejecución

```powershell
# Ejecutar todas las pruebas
.\.venv\Scripts\python.exe -m pytest -v

# Ejecutar con resumen
.\.venv\Scripts\python.exe -m pytest -q

# Ejecutar un archivo específico
.\.venv\Scripts\python.exe -m pytest tests/test_backend_services.py -v

# Preflight de publicación
powershell -ExecutionPolicy Bypass -File .\scripts\preflight_publicacion.ps1
```

### 1.3 Resultado actual

**227 tests y 7 subpruebas pasando** en 35 archivos de prueba.

---

## 2. Suite de pruebas actual

### 2.1 Backend

| Archivo | Cobertura |
|---------|-----------|
| `test_api.py` | Seguridad básica de API, endpoints con/sin token |
| `test_backend_schemas.py` | Validación Pydantic de schemas |
| `test_backend_services.py` | Servicios backend, rollback, transacciones |
| `test_backend_integration_sqlite.py` | Integración con SQLite temporal |
| `test_backend_pdf_service.py` | Validez, contenido variable y rendimiento de PDFs |
| `test_backend_dashboard_service.py` | Métricas de dashboard |
| `test_backend_view_contract.py` | Contrato de vista SQL |

### 2.2 Frontend

| Archivo | Cobertura |
|---------|-----------|
| `test_frontend_api_client.py` | Cliente API HTTP |
| `test_frontend_assets.py` | Rutas de assets |
| `test_flet_web.py` | Entrada Web, fábrica ASGI, entrega PDF y publicación de todos los assets |
| `test_frontend_components.py` | Componentes UI y cambio responsive móvil/escritorio/Web |
| `test_frontend_composition_analysis.py` | Análisis de composición corporal |
| `test_frontend_dashboard_redesign.py` | Dashboard y métricas |
| `test_frontend_formatters.py` | Formateo de valores |
| `test_frontend_form_helpers.py` | Helpers de formularios y payloads |
| `test_frontend_global_search.py` | Cierre del modal, navegación diferida y transmisión del deportista seleccionado |
| `test_frontend_interpretation.py` | Notas de interpretación clínica |
| `test_frontend_longitudinal_analysis.py` | Análisis longitudinal |
| `test_flet_web.py` | Entrega Web, apertura externa y compartir PDF Android con `FileProvider` |
| `test_frontend_navigation.py` | Navegación entre pantallas |
| `test_frontend_somatocarta.py` | Calibración y render de somatocarta |
| `test_frontend_table_builders.py` | Constructores de tablas |

### 2.3 Vistas

| Archivo | Cobertura |
|---------|-----------|
| `test_valoracion_view.py` | Vista de valoración corporal |
| `test_historial_layout.py` | Layout de historial |
| `test_deportistas_view.py` | CRUD y formulario móvil de cuatro pasos |
| `test_deportes_view.py` | Listado y CRUD móvil de deportes |
| `test_entidades_view.py` | Listado y CRUD móvil de entidades |
| `test_asignaciones_view.py` | Nombres, datos completos y CRUD móvil de asignaciones |
| `test_analisis_longitudinal_view.py` | Separación Web/móvil y conservación de todos los bloques longitudinales |
| `test_pdf_delivery_views.py` | Selección de descarga o compartir según plataforma |

### 2.4 Infraestructura

| Archivo | Cobertura |
|---------|-----------|
| `test_app_config.py` | Configuración de la app |
| `test_database_migrations.py` | Migraciones de base de datos |

### 2.5 E2E

| Archivo | Cobertura |
|---------|-----------|
| `test_e2e_workflow.py` | Login, fotografía, CRUD, asignación, valoración, edición, PDF individual/longitudinal y eliminación ordenada |

---

## 3. Casos de prueba funcionales

### 3.1 Autenticación

| ID | Caso | Paso | Resultado esperado |
|----|------|------|--------------------|
| AT-001 | Login correcto | Ingresar credenciales válidas | Token JWT, acceso al dashboard |
| AT-002 | Login incorrecto (usuario) | Ingresar usuario inexistente | Error 401, mensaje de error |
| AT-003 | Login incorrecto (password) | Ingresar contraseña errónea | Error 401, mensaje de error |
| AT-004 | Login campos vacíos | Dejar campos en blanco | Error 401/422 |
| AT-005 | Acceso sin token | Llamar endpoint protegido sin token | Error 401 |
| AT-006 | Token inválido | Usar token manipulado | Error 401 |
| AT-007 | Cerrar sesión | Pulsar botón de cerrar sesión | Limpieza de sesión, redirección a login |

### 3.2 CRUD Deportistas

| ID | Caso | Paso | Resultado esperado |
|----|------|------|--------------------|
| DP-001 | Crear deportista | Completar formulario y guardar | Deportista creado, aparece en lista |
| DP-002 | Deportista duplicado | Crear con ID existente | Error 400 |
| DP-003 | Campos obligatorios vacíos | Enviar sin nombre/ID/sexo | Error 422 |
| DP-004 | Sexo inválido | Ingresar sexo "X" | Error 422 |
| DP-005 | Email inválido | Ingresar email sin formato | Error 422 |
| DP-006 | Fecha futura | Ingresar fecha de nacimiento futura | Error 422 |
| DP-007 | Editar deportista | Modificar nombre y guardar | Nombre actualizado |
| DP-008 | Eliminar deportista | Pulsar eliminar y confirmar | Deportista eliminado |
| DP-009 | Buscar deportista | Escribir término de búsqueda | Lista filtrada |
| DP-010 | Paginación | Navegar entre páginas | Resultados paginados correctos |

### 3.3 CRUD Entidades

| ID | Caso | Paso | Resultado esperado |
|----|------|------|--------------------|
| EN-001 | Crear entidad | Completar formulario | Entidad creada |
| EN-002 | NIT duplicado | Crear con NIT existente | Error 400 |
| EN-003 | Editar entidad | Modificar y guardar | Actualización exitosa |
| EN-004 | Eliminar entidad | Eliminar entidad con asignaciones | HTTP 409; no elimina por `RESTRICT` |

### 3.4 CRUD Deportes

| ID | Caso | Paso | Resultado esperado |
|----|------|------|--------------------|
| DE-001 | Crear deporte | Ingresar nombre | Deporte creado |
| DE-002 | Deporte duplicado | Crear con nombre existente | HTTP 409; no crea duplicado |
| DE-003 | Editar deporte | Modificar nombre | Actualización exitosa |
| DE-004 | Eliminar deporte | Eliminar deporte con asignaciones | HTTP 409; no elimina por `RESTRICT` |

### 3.5 Valoraciones

| ID | Caso | Paso | Resultado esperado |
|----|------|------|--------------------|
| VA-001 | Crear valoración | Capturar mediciones y guardar | Valoración creada con detalles |
| VA-002 | Múltiples tomas | Agregar 3 tomas de medición | 3 detalles registrados |
| VA-003 | Valor fuera de rango | Ingresar estatura = 300 cm | Error 422 |
| VA-004 | Sin detalles | Guardar valoración sin tomas | Error 422 |
| VA-005 | Fecha duplicada | Crear 2 valoraciones misma fecha | Error por constraint único |
| VA-006 | Fecha futura | Ingresar fecha futura | Error 422 |
| VA-007 | Editar detalle | Modificar medición almacenada | Detalle actualizado |
| VA-008 | Agregar toma adicional | Crear 4ta toma en valoración existente | Detalle adicional creado |
| VA-009 | Eliminar detalle | Eliminar una toma específica | Toma eliminada |
| VA-010 | Eliminar valoración | Eliminar valoración completa | Valoración y detalles eliminados |

### 3.6 Análisis

| ID | Caso | Paso | Resultado esperado |
|----|------|------|--------------------|
| AN-001 | Historial individual | Buscar deportista con valoraciones | Lista de valoraciones con indicadores |
| AN-002 | Detalle de valoración | Seleccionar una valoración | Panel completo con composición, somatotipo, somatocarta |
| AN-003 | Análisis longitudinal | Buscar deportista con 2+ valoraciones | Gráficos de tendencia y somatocarta longitudinal |
| AN-004 | Longitudinal sin datos | Deportista con 1 valoración | Mensaje indicando que se requieren mínimo 2 |

### 3.7 PDFs

| ID | Caso | Paso | Resultado esperado |
|----|------|------|--------------------|
| PDF-001 | PDF individual | Descargar PDF de valoración | Archivo PDF válido (~1.7 MB) |
| PDF-002 | PDF longitudinal | Descargar PDF longitudinal | Archivo PDF válido (~1.7 MB) |
| PDF-003 | Contenido PDF | Verificar datos en el PDF | Nombre, ID, métricas presentes |
| PDF-004 | Compartir en Android | Pulsar Compartir PDF | Intent `ACTION_SEND`, MIME `application/pdf` y URI `content://` con permiso temporal |

---

## 4. Pruebas de integración con base de datos real

### 4.1 Requisitos

- Base de datos MySQL accesible.
- Variables de entorno configuradas en `.env`.

### 4.2 Casos

| ID | Caso | Descripción |
|----|------|-------------|
| INT-001 | Contrato de vista SQL | Verificar que `CDRVistaValoracionCorporal` tiene las 42 columnas esperadas |
| INT-002 | CRUD completo | Crear deportista, crear valoración, consultar historial, generar PDF, eliminar |
| INT-003 | Longitudinal completo | Crear 3 valoraciones con fechas diferentes, verificar análisis longitudinal |

---

## 5. Pruebas responsive

### 5.1 Resoluciones a evaluar

| Dispositivo | Resolución |
|-------------|-----------|
| Móvil pequeño | 320×568 |
| Móvil estándar | 375×667 |
| Tablet | 768×1024 |
| Laptop | 1366×768 |
| Escritorio | 1920×1080 |

La entrada Web debe probarse adicionalmente mediante `web_main:create_web_app`, respuesta HTTP y conexión WebSocket desde navegador.

### 5.2 Pantallas a evaluar

- Login
- Dashboard
- Deportistas (tabla y formulario)
- Valoración Corporal (wizard)
- Historial (master-detail)
- Análisis Longitudinal (gráficos)
- Entidades, Deportes, Asignaciones

---

## 6. Pruebas negativas

| ID | Caso | Resultado esperado |
|----|------|--------------------|
| NEG-001 | Token expirado | 401, mensaje de sesión expirada |
| NEG-002 | JSON malformado | 422 |
| NEG-003 | Campo con tipo incorrecto | 422 |
| NEG-004 | ID inexistente en GET | 404 |
| NEG-005 | Asignación duplicada | HTTP 409; no crea duplicado |
| NEG-006 | Deporte duplicado | HTTP 409; no crea duplicado |
| NEG-007 | Eliminar con referencias | HTTP 409 y política MySQL `RESTRICT` |

---

## 7. Criterios de aceptación de pruebas

- Todos los tests automatizados deben pasar (227/227 y 7 subpruebas).
- Los flujos funcionales críticos deben operar sin errores.
- Los PDFs generados deben ser válidos y contener los datos correctos.
- La interfaz debe ser usable en las 5 resoluciones objetivo.

---

*Este plan se actualiza con cada versión del sistema.*
