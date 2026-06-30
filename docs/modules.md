# Módulos funcionales — Somatocarta v1.2.11

**Fecha:** 30 de junio de 2026

---

> Actualizado el 30 de junio de 2026. La interfaz móvil y la interfaz Web comparten reglas de negocio y API, pero mantienen composiciones visuales independientes.

## 1. Autenticación (Login)

| Campo | Detalle |
|-------|---------|
| **Propósito** | Controlar el acceso al sistema mediante credenciales de usuario. |
| **Usuarios involucrados** | Todos los usuarios del sistema. |
| **Pantallas/rutas** | `main.py` (pantalla de login), `POST /auth/login` |
| **Entradas** | Usuario (LOGIN_USER), contraseña (PSW_USER). |
| **Procesos** | Verificación de credenciales, generación de token JWT HS256 configurable mediante `ACCESS_TOKEN_EXPIRE_MINUTES` (30 min por defecto), registro en auditoría. |
| **Salidas** | Token de acceso, nombre de usuario, ID de usuario. Sesión almacenada en Flet. |
| **Validaciones** | Credenciales no vacías. Usuario debe existir. Contraseña debe coincidir. |
| **Dependencias** | `src/backend/auth_utils.py`, `src/backend/routers/auth.py`, tabla `CDRTablaUsuarios`. |
| **Estado** | Funcional. Contraseñas en texto plano por compatibilidad heredada. |
| **Pendientes** | Migración a hash seguro. Control de roles. |

---

## 2. Dashboard

| Campo | Detalle |
|-------|---------|
| **Propósito** | Mostrar resumen operativo del sistema al iniciar sesión. |
| **Usuarios involucrados** | Todos los usuarios autenticados. |
| **Pantallas/rutas** | `views/dashboard.py`, `GET /dashboard/summary` |
| **Entradas** | Token de autenticación. |
| **Procesos** | Consulta de totales operativos, validación de contrato de vista SQL y construcción de accesos rápidos a módulos. |
| **Salidas** | Tarjetas de métricas, indicador de salud y tarjetas de navegación con iconos Material vectoriales. |
| **Validaciones** | Token válido. |
| **Dependencias** | `src/backend/services/dashboard_service.py`, `src/backend/services/view_contract_service.py`. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales; mantener validación visual responsive. |

---

## 3. Menú principal / Navegación

| Campo | Detalle |
|-------|---------|
| **Propósito** | Proveer navegación entre todos los módulos del sistema. |
| **Usuarios involucrados** | Todos los usuarios autenticados. |
| **Pantallas/rutas** | `src/frontend/app_shell.py`, `src/frontend/navigation.py` |
| **Entradas** | Selección de módulo por el usuario. |
| **Procesos** | Sidebar responsive (desktop) o menú hamburguesa (móvil), historial de rutas y carga diferida de vistas. |
| **Salidas** | Cambio de pantalla con contexto limpio. |
| **Módulos accesibles** | Dashboard, Deportistas, Valoración Corporal, Historial, Análisis Longitudinal, Entidades, Deportes, Asignaciones, Acerca del Proyecto. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales. Mantener pruebas de navegación y resize. |

---

## 4. Deportistas (CRUD)

| Campo | Detalle |
|-------|---------|
| **Propósito** | Gestionar el registro de deportistas con datos personales, demográficos y de contacto. |
| **Usuarios involucrados** | Evaluadores, administradores. |
| **Pantallas/rutas** | `views/deportistas.py`, `/deportistas/` |
| **Entradas** | Identificación, tipo documento, nombre, sexo, fecha nac., dirección, ciudad, departamento, país, teléfono, email, estrato, nivel educativo, institución, observaciones, fotografía. |
| **Procesos** | Crear, listar paginado, buscar por nombre/ID, consultar detalle, editar, eliminar. Carga de fotografía con validación. |
| **Salidas** | Lista paginada de deportistas, formulario de creación/edición, confirmación de operaciones. |
| **Validaciones** | ID obligatorio (máx 20), nombre obligatorio (máx 50), sexo M/F, email válido, fecha nac. no futura. |
| **Dependencias** | Catálogos de tipos de documento, estratos, niveles educativos. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales. La API y MySQL bloquean eliminaciones con dependencias mediante `RESTRICT` y HTTP 409. |

En móvil, el alta y la edición se distribuyen en cuatro pasos: datos básicos, contacto/ubicación, información socioeconómica y fotografía.

---

## 5. Entidades (CRUD)

En móvil, las entidades se presentan como tarjetas por razón social/NIT y el formulario separado conserva NIT, razón social, teléfono, contacto y correo.

| Campo | Detalle |
|-------|---------|
| **Propósito** | Gestionar entidades deportivas (ligas, clubes, instituciones). |
| **Usuarios involucrados** | Administradores. |
| **Pantallas/rutas** | `views/entidades.py`, `/entidades/` |
| **Entradas** | NIT, razón social, teléfono, contacto, email. |
| **Procesos** | Crear, listar paginado, buscar, editar, eliminar. |
| **Salidas** | Lista paginada, formulario de creación/edición. |
| **Validaciones** | NIT obligatorio (máx 20), razón social obligatoria (máx 50), email válido si se proporciona. NIT único. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales. La eliminación con asignaciones se bloquea mediante `RESTRICT` y HTTP 409. |

---

## 6. Deportes (CRUD)

En móvil, cada tarjeta muestra nombre e ID y abre el formulario de edición/eliminación; el botón inferior abre un alta nueva.

| Campo | Detalle |
|-------|---------|
| **Propósito** | Gestionar el catálogo de deportes. |
| **Usuarios involucrados** | Administradores. |
| **Pantallas/rutas** | `views/deportes.py`, `/deportes/` |
| **Entradas** | Nombre del deporte, ID opcional. |
| **Procesos** | Crear, listar paginado, buscar, editar, eliminar. |
| **Salidas** | Lista paginada, formulario de creación/edición. |
| **Validaciones** | Nombre obligatorio (máx 50) y único sin distinguir mayúsculas/minúsculas. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales. Los duplicados se bloquean en servicio y base de datos. |

---

## 7. Asignaciones (CRUD)

En móvil, las tarjetas muestran nombre del deportista, deporte y entidad. La edición recupera el registro completo del deportista para presentar fecha, correo y ubicación.

| Campo | Detalle |
|-------|---------|
| **Propósito** | Relacionar deportistas con entidades y deportes. |
| **Usuarios involucrados** | Evaluadores, administradores. |
| **Pantallas/rutas** | `views/asignaciones.py`, `/asignaciones/` |
| **Entradas** | Deportista (búsqueda), deporte (dropdown), entidad (dropdown). |
| **Procesos** | Crear, listar paginado, buscar, editar, eliminar. Validación de referencias (deportista, deporte, entidad deben existir). |
| **Salidas** | Lista paginada de asignaciones, formulario de creación/edición. |
| **Validaciones** | IDs obligatorios, referencias existentes y combinación deporte/deportista/entidad única. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales. Duplicados e integridad referencial están protegidos en API y MySQL. |

---

## 8. Valoración Corporal

| Campo | Detalle |
|-------|---------|
| **Propósito** | Capturar mediciones antropométricas de un deportista y registrar una valoración completa. |
| **Usuarios involucrados** | Evaluadores corporales. |
| **Pantallas/rutas** | `views/valoracion.py`, `POST /somatotipo/` |
| **Entradas** | Deportista (búsqueda), fecha, 14 campos de medición por toma, observaciones. |
| **Procesos** | Wizard de 2 pasos (captura / revisión). Búsqueda de deportista con tarjeta informativa. Validación en tiempo real de rangos. Soporte para múltiples tomas (agregar, editar, eliminar, duplicar). Carga de valoraciones almacenadas para edición. Prevención de duplicados por fecha. |
| **Salidas** | Valoración guardada con encabezado y detalles. Confirmación visual. |
| **Validaciones** | 14 campos con rangos definidos en `src/anthropometry.py`. Fecha no futura. Deportista debe existir. |
| **Dependencias** | `src/anthropometry.py` (reglas de validación), `src/backend/services/somatotipo_service.py`. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales. Edición, creación y eliminación de tomas están cubiertas por integración y E2E. |

---

## 9. Análisis de Valoración Corporal (Historial)

| Campo | Detalle |
|-------|---------|
| **Propósito** | Mostrar los resultados calculados de una valoración corporal: composición corporal, somatotipo, somatocarta. |
| **Usuarios involucrados** | Evaluadores, entrenadores, investigadores. |
| **Pantallas/rutas** | `views/historial.py`, `GET /somatotipo/vista/deportista/{identi}` |
| **Entradas** | Deportista (búsqueda). |
| **Procesos** | Listado paginado de valoraciones (master-detail). Detalle con KPIs, medidas, Yuhasz como método principal, Faulkner como comparación, masas, balance, IMC, complexión, somatotipo, somatocarta, PDF y eliminación confirmada. |
| **Salidas** | Panel de análisis completo con gráficos, tablas y somatocarta. |
| **Validaciones** | Layout master-detail adaptativo (escritorio: simultáneo; móvil: toggle). |
| **Dependencias** | Vista SQL `CDRVistaValoracionCorporal`, `src/frontend/composition_analysis.py`, `src/frontend/somatocarta.py`. |
| **Estado** | Funcional. |
| **Pendientes** | Obtener aprobación metodológica formal del equipo de ciencias del deporte. La base activa ya tiene aplicada y verificada la migración `004`. |

---

## 10. Análisis Longitudinal

| Campo | Detalle |
|-------|---------|
| **Propósito** | Comparar la evolución temporal de los indicadores de un deportista a través de múltiples valoraciones. |
| **Usuarios involucrados** | Entrenadores, investigadores. |
| **Pantallas/rutas** | `views/analisis_longitudinal.py`, `GET /somatotipo/vista/deportista/{identi}/longitudinal/pdf` |
| **Entradas** | Deportista (búsqueda) con mínimo 2 valoraciones. |
| **Procesos** | Tarjetas KPI (valor inicial, final, delta, % cambio). Gráficos de línea para 10 variables. Comparación de métodos de grasa. Somatocarta longitudinal con trayectoria cronológica. Gráfico peso vs masa muscular. Tabla histórica. PDF longitudinal. |
| **Diseño por plataforma** | Web presenta el panel analítico amplio; móvil conserva todos los datos en secciones compactas con selector de variable y desplazamiento vertical. |
| **Variables graficables** | Peso, IMC, % graso Yuhasz, % graso Faulkner, masa muscular, endomorfismo, mesomorfismo, ectomorfismo, masa ósea y masa residual. |
| **Salidas** | Panel de análisis longitudinal interactivo con gráficos y PDF. |
| **Validaciones** | Requiere mínimo 2 valoraciones. |
| **Dependencias** | `src/frontend/longitudinal_analysis.py`. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales. Mantener pruebas de series, coordenadas y PDF longitudinal. |

---

## 11. Informes PDF

| Campo | Detalle |
|-------|---------|
| **Propósito** | Generar informes profesionales en formato PDF de valoraciones individuales y análisis longitudinales. |
| **Usuarios involucrados** | Evaluadores, entrenadores, investigadores. |
| **Pantallas/rutas** | `GET /somatotipo/{id}/pdf`, `GET /somatotipo/vista/deportista/{identi}/longitudinal/pdf` |
| **Entradas** | ID de somatotipo (individual) o identificación de deportista (longitudinal). |
| **Procesos** | Generación manual de PDF 1.4. Pillow optimiza imágenes y el decodificador PNG interno queda como fallback. Inclusión de datos del deportista, métricas, mediciones, composición corporal, somatotipo, somatocarta y gráficos. |
| **Salidas** | Web descarga el archivo; escritorio lo abre externamente; Android puede abrirlo o compartirlo con aplicaciones instaladas mediante el selector del sistema. |
| **Dependencias** | `src/backend/services/pdf_service.py`, Pillow para imágenes y fallback PNG interno. |
| **Estado** | Funcional. Los PDFs contienen los datos correctos del deportista. |
| **Pendientes** | Sin pendientes funcionales. Mantener pruebas de variabilidad y rendimiento. |

---

## 12. Composición Corporal

| Campo | Detalle |
|-------|---------|
| **Propósito** | Analizar y comparar los métodos de estimación de grasa corporal y la distribución de masas. |
| **Usuarios involucrados** | Evaluadores, investigadores. |
| **Pantallas/rutas** | Panel dentro de `views/historial.py`. |
| **Entradas** | Datos calculados desde la vista SQL. |
| **Procesos** | Yuhasz como método principal para deportistas y Faulkner como comparación. Cálculo de distribución de masas (grasa, muscular, ósea, residual). Validación de balance de masas (umbral 5%). Gráfico de pastel de distribución. |
| **Salidas** | Tablas comparativas, gráfico de pastel, mensaje de validación de balance. |
| **Dependencias** | `src/frontend/composition_analysis.py`. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales. La metodología clínica sigue sujeta a aprobación profesional. |

---

## 13. Somatotipo y Somatocarta

| Campo | Detalle |
|-------|---------|
| **Propósito** | Mostrar los componentes del somatotipo (Heath-Carter) y ubicar al deportista en la carta de somatotipos. |
| **Usuarios involucrados** | Evaluadores, entrenadores. |
| **Pantallas/rutas** | Panel dentro de `views/historial.py`. |
| **Entradas** | Coordenadas X, Y calculadas desde la vista SQL. |
| **Procesos** | Render de imagen de somatocarta (`Somatocarta.png`). Calibración por interpolación de marcas de ejes. Mapeo de coordenadas a píxeles. Render de marcador del deportista con etiqueta y badge. |
| **Salidas** | Gráfico de somatocarta con ubicación del deportista. |
| **Dependencias** | `src/frontend/somatocarta.py`, `assets/Somatocarta.png`. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales. Fórmulas y coordenadas verificadas contra la calculadora Python. |

---

## 14. IMC

| Campo | Detalle |
|-------|---------|
| **Propósito** | Mostrar el índice de masa corporal y su clasificación. |
| **Usuarios involucrados** | Evaluadores, entrenadores. |
| **Pantallas/rutas** | Panel dentro de `views/historial.py`. |
| **Entradas** | IMC y EstadoIMC desde la vista SQL. |
| **Procesos** | Visualización del valor IMC con su estado (Bajo peso, Normal, Sobrepeso, Obesidad). Imagen de referencia. Nota metodológica para menores de edad. |
| **Salidas** | Tarjeta de IMC con clasificación e imagen de referencia. |
| **Dependencias** | `src/frontend/interpretation.py`. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales. Mantener criterios diferenciados para menores de edad. |

---

## 15. Contextura Física

| Campo | Detalle |
|-------|---------|
| **Propósito** | Mostrar el índice de complexión física y su clasificación. |
| **Usuarios involucrados** | Evaluadores. |
| **Pantallas/rutas** | Panel dentro de `views/historial.py`. |
| **Entradas** | Complexion y TipoComplexion desde la vista SQL. |
| **Procesos** | Visualización del valor de complexión con su tipo (Pequeña, Mediana, Grande). Imagen de referencia. |
| **Salidas** | Tarjeta de complexión con imagen de referencia. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales. |

---

## 16. Sección Acerca del Proyecto

| Campo | Detalle |
|-------|---------|
| **Propósito** | Mostrar información institucional del proyecto. |
| **Usuarios involucrados** | Todos los usuarios. |
| **Pantallas/rutas** | `views/acerca.py` |
| **Entradas** | N/A (contenido estático). |
| **Procesos** | Muestra descripción del proyecto, alcance y logotipos institucionales (CDR, ISC, UTP, Nyquist). |
| **Salidas** | Pantalla informativa. |
| **Estado** | Funcional. |
| **Pendientes** | Sin pendientes funcionales. |

---

## 17. Sistema de Auditoría

| Campo | Detalle |
|-------|---------|
| **Propósito** | Registrar todas las operaciones críticas del sistema para trazabilidad y seguridad. |
| **Usuarios involucrados** | Sistema (automático). |
| **Pantallas/rutas** | `src/backend/audit.py`, tabla `CDRTablaAuditoria`, archivo `audit.log`. |
| **Entradas** | Cada operación auditada en routers. |
| **Procesos** | Registro dual (base de datos + archivo log). Captura de: timestamp UTC, actor, código de acción, recurso, HTTP method/endpoint/status, IP cliente, user agent, correlation ID, request/response JSON (contraseñas enmascaradas). |
| **Operaciones auditadas** | LOGIN_SUCCESS, LOGIN_FAILED, CREATE/UPDATE/DELETE_DEPORTISTA, CREATE/UPDATE/DELETE_SOMATOTIPO, CREATE/UPDATE/DELETE_SOMATOTIPO_DETALLE, DOWNLOAD_PDF_VALORACION, DOWNLOAD_PDF_LONGITUDINAL. |
| **Salidas** | Registros en `CDRTablaAuditoria` y `audit.log`. |
| **Estado** | Funcional. |
| **Pendientes** | No hay interfaz para consultar los registros de auditoría. |

---

## 18. Responsive Design

| Campo | Detalle |
|-------|---------|
| **Propósito** | Adaptar la interfaz a diferentes tamaños de pantalla. |
| **Usuarios involucrados** | Todos los usuarios. |
| **Implementación** | `src/frontend/components.py` (helpers responsive), `src/frontend/app_shell.py` (sidebar vs menú/navegación inferior) y ramas móviles explícitas en vistas con flujos distintos a Web. |
| **Breakpoints** | xs (móvil pequeño), sm (móvil grande), md (tablet), lg (escritorio). |
| **Comportamiento** | Escritorio: sidebar + master-detail simultáneo. Móvil/tablet: menú hamburguesa + toggle entre lista y detalle. |
| **Estado** | Implementado con cambio dinámico entre sidebar y menú móvil, compartido por Android, escritorio y Flet Web. Assets y login Web fueron verificados en Chrome móvil. |
| **Pendientes** | Validación visual autenticada final en navegadores, tablet y dispositivos Android adicionales. |

---

## 19. Gestión de Usuarios

| Campo | Detalle |
|-------|---------|
| **Propósito** | Administrar credenciales, roles y accesos del sistema. |
| **Usuarios involucrados** | Administrador del sistema. |
| **Pantallas/rutas** | No existe pantalla actualmente. Gestionado directamente en BD (`CDRTablaUsuarios`). |
| **Entradas** | Credenciales de usuario, tipo de usuario. |
| **Procesos** | Autenticación y cruce de datos en vista `CDRVistaValoracionCorporal`. |
| **Salidas** | N/A en UI actualmente. |
| **Estado** | No implementado en ninguna interfaz (Android, escritorio ni Web). |
| **Pendientes** | Desarrollar módulo CRUD de gestión de usuarios, roles (Administrador, Evaluador) y migrar contraseñas a Hash. |

---

## 20. Pruebas o QA y Scripts

| Campo | Detalle |
|-------|---------|
| **Propósito** | Garantizar la estabilidad funcional, cálculos matemáticos e integridad de la aplicación. |
| **Usuarios involucrados** | Desarrolladores, Analistas QA. |
| **Rutas/Carpetas** | `tests/`, `scripts/`. |
| **Entradas** | Scripts de Python (pytest), scripts de PowerShell. |
| **Procesos** | Ejecución de pruebas unitarias, de integración y endpoints. Migración y mantenimiento mediante scripts auxiliares. |
| **Salidas** | Reportes de cobertura (236 tests, 7 subpruebas y 74% global), E2E crítico y estado del preflight. |
| **Dependencias** | `pytest`, base de datos SQLite temporal en entorno de pruebas. |
| **Estado** | Implementado y funcional. |
| **Pendientes** | Ampliar cobertura de pruebas E2E visuales para UI responsive. |
