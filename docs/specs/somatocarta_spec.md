# Somatocarta — Software Specification (Spec Kit)

**Versión:** 1.0
**Fecha:** 22 de junio de 2026
**Estado:** Vigente

---

## 1. Overview

### 1.1 Nombre del sistema

Somatocarta — Aplicación de Valoración Corporal y Somatotipo.

### 1.2 Propósito

Somatocarta es una aplicación de escritorio/móvil para registrar deportistas, capturar valoraciones antropométricas, calcular indicadores de composición corporal y somatotipo, generar análisis individuales y longitudinales, y producir informes PDF profesionales.

### 1.3 Contexto institucional

Somatocarta forma parte de **SINVADE — Sistema Integral de Valoración Deportiva**, un ecosistema de herramientas para la evaluación científica del deportista.

Instituciones vinculadas:

- Grupo de Investigación y Desarrollo en Cultura de la Salud.
- Grupo de Investigación Nyquist.
- Laboratorio de Movimiento Humano.
- Programa de Ciencias del Deporte — Facultad de Ciencias de la Salud.
- Programa de Ingeniería de Sistemas y Computación — Facultad de Ingenierías.
- Universidad Tecnológica de Pereira.
- Centro de Alto Rendimiento (CDR).
- Instituto Superior de Ciencias (ISC).

### 1.4 Usuarios objetivo

- Evaluadores corporales / profesionales de ciencias del deporte.
- Entrenadores deportivos.
- Administradores del sistema.
- Investigadores.

### 1.5 Alcance actual

Versión **v1.2.5**. Aplicación funcional con frontend Flet (multiplataforma, incluyendo Android) y backend FastAPI con base de datos MySQL.

---

## 2. Problem Statement

### 2.1 Problema que resuelve

El proceso manual de valoración corporal deportiva implica registro en papel, cálculo manual de indicadores, y generación artesanal de informes. Esto genera:

- Errores de cálculo en fórmulas antropométricas.
- Pérdida de historial de mediciones.
- Imposibilidad de análisis longitudinal eficiente.
- Dificultad para comparar métodos de estimación de grasa corporal.
- Informes inconsistentes en formato y contenido.

### 2.2 Necesidad de valoración corporal digital

Los profesionales del deporte necesitan una herramienta que:

- Capture mediciones antropométricas de forma estructurada.
- Calcule automáticamente indicadores derivados (IMC, % graso, somatotipo, masas corporales).
- Permita seguimiento temporal de cada deportista.
- Genere informes profesionales reproducibles.
- Funcione en entornos de campo (dispositivos móviles).

### 2.3 Limitaciones del proceso manual

- Cálculos repetitivos y propensos a error.
- Sin trazabilidad de quién registró y cuándo.
- Sin validación de rangos plausibles.
- Sin gráficos ni visualización de tendencias.

---

## 3. Goals

| ID | Meta |
|----|------|
| G-001 | Registrar deportistas con datos personales, demográficos y de contacto. |
| G-002 | Gestionar entidades deportivas (ligas, clubes, instituciones). |
| G-003 | Gestionar catálogo de deportes. |
| G-004 | Asignar deportistas a entidades y deportes. |
| G-005 | Registrar valoraciones corporales con múltiples tomas de medición. |
| G-006 | Calcular indicadores antropométricos: IMC, composición corporal, somatotipo. |
| G-007 | Generar análisis individual de valoración corporal. |
| G-008 | Generar análisis longitudinal con gráficos de tendencia. |
| G-009 | Generar informes PDF individuales y longitudinales. |
| G-010 | Visualizar somatocarta (carta de Heath-Carter) con ubicación del deportista. |
| G-011 | Soportar ejecución en escritorio y dispositivos móviles (Android). |
| G-012 | Proveer auditoría de operaciones críticas. |
| G-013 | Mejorar la experiencia de usuario con diseño responsive. |

---

## 4. Non-Goals

| ID | No-objetivo | Razón |
|----|-------------|-------|
| NG-001 | No reemplaza el diagnóstico médico profesional. | Los cálculos son estimaciones antropométricas, no diagnósticos clínicos. |
| NG-002 | No prescribe entrenamiento automáticamente. | Fuera del alcance actual. |
| NG-003 | No realiza análisis clínico especializado (sangre, genética, etc.). | Solo antropometría. |
| NG-004 | No mezcla análisis individual con análisis longitudinal en una sola vista. | Son contextos diferentes que requieren separación conceptual. |
| NG-005 | No modifica cálculos sin validación profesional. | Los cálculos viven en la vista SQL y requieren auditoría clínica antes de cambios. |
| NG-006 | No gestiona horarios ni agendas de entrenamiento. | Fuera del alcance. |
| NG-007 | No reemplaza la valoración presencial por un profesional. | Es una herramienta de registro y análisis, no de evaluación. |
| NG-008 | No soporta categorías de peso deportivas (ej. boxeo). | Pendiente de implementación futura. |

---

## 5. Personas / Users

### 5.1 Administrador del sistema

- **Perfil:** Personal técnico con acceso completo al sistema.
- **Responsabilidades:** Gestionar usuarios, configurar parámetros, supervisar operaciones.
- **Necesidades:** Control total del sistema, auditoría, gestión de datos maestros.

### 5.2 Evaluador corporal

- **Perfil:** Profesional de ciencias del deporte o estudiante avanzado.
- **Responsabilidades:** Realizar valoraciones antropométricas, registrar mediciones.
- **Necesidades:** Formularios eficientes, validación de datos, acceso a historial.

### 5.3 Entrenador

- **Perfil:** Entrenador deportivo que necesita seguimiento de deportistas.
- **Responsabilidades:** Consultar evolución de deportistas, revisar informes.
- **Necesidades:** Análisis longitudinal, PDFs, dashboard resumen.

### 5.4 Investigador

- **Perfil:** Investigador del grupo Nyquist o vinculado a SINVADE.
- **Responsabilidades:** Analizar datos de población deportiva, validar metodologías.
- **Necesidades:** Exportación de datos, análisis estadístico, trazabilidad.

### 5.5 Deportista (indirecto)

- **Perfil:** Deportista registrado en el sistema.
- **Interacción:** No accede directamente al sistema. Es sujeto de valoración.
- **Necesidades:** Que sus datos sean precisos y confidenciales.

---

## 6. User Stories

### Autenticación

```text
US-001: Como usuario, quiero iniciar sesión con mis credenciales para acceder al sistema.
US-002: Como usuario, quiero que mi sesión expire después de un tiempo de inactividad para proteger mis datos.
US-003: Como usuario, quiero cerrar sesión explícitamente cuando termine mi sesión de trabajo.
```

### Dashboard

```text
US-004: Como usuario, quiero ver un resumen del sistema al iniciar sesión para conocer el estado general.
US-005: Como usuario, quiero identificar rápidamente el estado del sistema y sus módulos principales.
US-006: Como usuario, quiero acceder rápidamente a los módulos principales desde el dashboard.
```

### Deportistas

```text
US-007: Como evaluador, quiero registrar un deportista nuevo con sus datos personales y demográficos.
US-008: Como evaluador, quiero buscar deportistas por nombre o identificación.
US-009: Como evaluador, quiero editar los datos de un deportista existente.
US-010: Como evaluador, quiero cargar una fotografía del deportista.
US-011: Como administrador, quiero eliminar un deportista que fue registrado por error.
```

### Entidades

```text
US-012: Como administrador, quiero registrar entidades deportivas (ligas, clubes).
US-013: Como administrador, quiero editar la información de una entidad.
US-014: Como administrador, quiero buscar entidades por nombre o NIT.
```

### Deportes

```text
US-015: Como administrador, quiero registrar deportes en el catálogo.
US-016: Como administrador, quiero editar el nombre de un deporte.
```

### Asignaciones

```text
US-017: Como evaluador, quiero asignar un deportista a una entidad y un deporte.
US-018: Como evaluador, quiero ver las asignaciones de un deportista.
US-019: Como evaluador, quiero editar o eliminar una asignación.
```

### Valoración corporal

```text
US-020: Como evaluador, quiero registrar una valoración corporal con múltiples tomas de medición.
US-021: Como evaluador, quiero que el sistema valide los rangos de las mediciones antropométricas.
US-022: Como evaluador, quiero agregar, editar y eliminar tomas antes de guardar la valoración.
US-023: Como evaluador, quiero cargar una valoración almacenada para editar sus mediciones.
US-024: Como evaluador, quiero eliminar una valoración completa si fue registrada por error.
```

### Análisis individual

```text
US-025: Como evaluador, quiero consultar el análisis de una valoración para ver composición corporal y somatotipo.
US-026: Como evaluador, quiero ver la somatocarta con la ubicación del deportista.
US-027: Como evaluador, quiero descargar un PDF con los resultados de la valoración.
```

### Análisis longitudinal

```text
US-028: Como entrenador, quiero ver la evolución temporal de los indicadores de un deportista.
US-029: Como entrenador, quiero comparar gráficos de peso, IMC, % graso y somatotipo a lo largo del tiempo.
US-030: Como entrenador, quiero descargar un PDF del análisis longitudinal.
```

---

## 7. Functional Requirements

### FR-001: Autenticación

El sistema debe permitir inicio de sesión con usuario y contraseña, generar token JWT, y proteger todas las rutas privadas.

### FR-002: Dashboard

El sistema debe mostrar métricas operativas, estado de salud de la vista SQL y accesos rápidos a los módulos principales.

### FR-003: CRUD de deportistas

El sistema debe permitir crear, listar, buscar, consultar, editar y eliminar deportistas con validación de campos obligatorios, formato de email, sexo (M/F), y fecha de nacimiento no futura.

### FR-004: CRUD de entidades

El sistema debe permitir crear, listar, buscar, editar y eliminar entidades deportivas con validación de NIT único.

### FR-005: CRUD de deportes

El sistema debe permitir crear, listar, buscar, editar y eliminar deportes del catálogo.

### FR-006: CRUD de asignaciones

El sistema debe permitir crear, listar, editar y eliminar asignaciones deportista-entidad-deporte, validando que el deportista, la entidad y el deporte existan.

### FR-007: Registro de valoración corporal

El sistema debe permitir registrar una valoración con encabezado (fecha, deportista, observaciones) y uno o más detalles de medición antropométrica (14 campos).

### FR-008: Validación de mediciones

El sistema debe validar que cada medición antropométrica esté dentro de los rangos definidos:
- Estatura: >50 y ≤250 cm
- Peso: >10 y ≤300 kg
- Pliegues: >0 y ≤100 mm
- Diámetros: >0 y ≤200 mm
- Perímetros: >0 y ≤250 cm
- Circunferencia carpo: >0 y ≤200 mm

### FR-009: Múltiples tomas de medición

El sistema debe permitir registrar múltiples tomas (repeticiones) por valoración, con posibilidad de agregar, editar y eliminar tomas individuales.

### FR-010: Historial de valoraciones

El sistema debe mostrar el historial paginado de valoraciones de un deportista con todos los indicadores calculados desde la vista SQL.

### FR-011: Análisis de composición corporal

El sistema debe mostrar Yuhasz como método principal para población deportiva y Faulkner como referencia comparativa, calcular masas corporales (grasa, muscular, ósea, residual), validar balance de masas, y generar gráfico de distribución.

### FR-012: Análisis de somatotipo

El sistema debe mostrar componentes de somatotipo (endomorfismo, mesomorfismo, ectomorfismo) con escalas descriptivas y coordenadas X/Y para la somatocarta.

### FR-013: Somatocarta

El sistema debe renderizar la carta de Heath-Carter con calibración por interpolación de marcas, ubicar al deportista según sus coordenadas, y mostrar etiqueta y badge.

### FR-014: Análisis longitudinal

El sistema debe permitir comparar valoraciones temporales de un deportista, graficar 10 variables, mostrar tarjetas de cambio, y renderizar somatocarta longitudinal con trayectoria.

### FR-015: Informes PDF

El sistema debe generar PDFs individuales de valoración y longitudinales con datos del deportista, métricas, composición corporal, mediciones, somatotipo, somatocarta y gráficos.

### FR-016: Catálogos

El sistema debe proveer catálogos de tipos de documento, estratos socioeconómicos y niveles educativos.

### FR-017: Carga de fotografías

El sistema debe permitir cargar fotografías JPG/PNG con validación de extensión, tipo MIME y tamaño máximo (5 MB).

### FR-018: Auditoría

El sistema debe registrar en base de datos y archivo de log las operaciones de login (exitoso/fallido), CRUD de deportistas, operaciones de somatotipo, y descargas de PDF.

### FR-019: Diseño responsive

El sistema debe adaptar su interfaz a dispositivos móviles, tabletas y escritorio.

### FR-020: Sección Acerca de

El sistema debe mostrar información del proyecto, su propósito y logotipos institucionales.

---

## 8. Non-Functional Requirements

### Usabilidad

```text
NFR-001: La interfaz debe usar un lenguaje claro y consistente en español.
NFR-002: Los formularios deben indicar campos obligatorios con asterisco (*).
NFR-003: Los mensajes de error deben ser específicos y orientados a la acción.
NFR-004: Los estados vacíos deben mostrar mensajes informativos.
NFR-005: Las acciones destructivas deben solicitar confirmación.
```

### Accesibilidad

```text
NFR-006: Los formularios deben ser navegables por teclado.
NFR-007: Los colores deben tener contraste suficiente para legibilidad.
```

### Responsive

```text
NFR-008: La interfaz debe adaptarse a pantallas de 320px a 1920px de ancho.
NFR-009: No debe aparecer scroll horizontal no deseado en vistas principales.
NFR-010: Las tablas deben permitir scroll horizontal cuando no quepan en pantalla.
NFR-011: El layout master-detail debe alternar a modo toggle en móvil/tablet.
```

### Seguridad

```text
NFR-012: Todas las rutas privadas deben requerir token JWT válido.
NFR-013: Los tokens deben expirar después de un tiempo definido.
NFR-014: Las contraseñas no deben transmitirse en texto plano en la red (solo dentro de la BD por compatibilidad heredada).
NFR-015: El sistema debe registrar intentos de login fallidos.
```

### Rendimiento

```text
NFR-016: Los listados deben usar paginación para evitar consultas masivas.
NFR-017: Las imágenes deben optimizarse para no exceder 5 MB.
NFR-018: El PDF individual debe generarse en menos de 10 segundos.

NFR-019: La expiración JWT debe configurarse mediante `ACCESS_TOKEN_EXPIRE_MINUTES`, con 30 minutos por defecto y un mínimo técnico de 1 minuto.
```

### Mantenibilidad

```text
NFR-019: La lógica de negocio debe residir en servicios, no en routers.
NFR-020: El frontend no debe usar requests directamente fuera de ApiClient.
NFR-021: Los schemas Pydantic deben vivir fuera de los routers.
```

### Trazabilidad

```text
NFR-022: Las operaciones CRUD deben registrarse en la tabla de auditoría.
NFR-023: Cada valoración debe registrar el usuario que la creó.
```

### Compatibilidad

```text
NFR-024: La aplicación debe ejecutarse en Windows, Linux y Android.
NFR-025: El backend debe ser compatible con MySQL 5.7+ y 8.0+.
```

---

## 9. Domain Model

### 9.1 Entidades principales

```text
┌─────────────────┐
│   TipoUser      │
│─────────────────│
│ id_Tipo_User(PK)│
│ Tipo_User       │
└────────┬────────┘
         │ 1
         │
┌────────▼────────┐     ┌──────────────────────┐
│   Usuario       │     │  TipoDocumento       │
│─────────────────│     │──────────────────────│
│ ID_USER (PK)    │     │ TIPO_IDENTI (PK)     │
│ LOGIN_USER      │     │ NOMBRE_IDENTI        │
│ PSW_USER        │     └──────────┬───────────┘
│ NOM_USER        │                │ 1
│ MAIL_USER       │                │
│ ID_TIPO_USER(FK)│     ┌──────────▼───────────┐
└─────────────────┘     │   Deportista         │
                        │──────────────────────│
┌─────────────────┐     │ IDENTI_DEPORTISTA(PK)│
│   Entidad       │     │ TIPO_IDENTI (FK)     │
│─────────────────│     │ NOMBRE_DEPORTISTA    │
│ NIT_ENTIDAD(PK) │     │ SEXO_DEPORTISTA      │
│ RAZON_SOCIAL    │     │ FECHA_NAC            │
│ TELEFONO        │     │ FOTO_DEPORTISTA      │
│ CONTACTO        │     │ CIUDAD_NAC           │
│ E_MAIL          │     │ DEPARTA_NAC          │
└────────┬────────┘     │ PAIS_NAC             │
         │              │ CIUDAD_RESI          │
         │              │ DEPARTA_RESI         │
┌────────▼────────┐     │ DIRECC_RESI          │
│   Deporte       │     │ E_MAIL               │
│─────────────────│     │ ID_ESTRATO (FK)      │
│ ID_DEPORTE (PK) │     │ ID_NIVEL (FK)        │
│ DEPORTE         │     │ NOMBRE_INSTITU       │
└────────┬────────┘     │ OBSERVACIONES        │
         │              └──────────┬───────────┘
         │                         │
         │    ┌────────────────────▼─────┐
         └───►│  DeporteDeportista       │
              │──────────────────────────│
              │ id (PK)                  │
              │ ID_DEPORTE (FK)          │
              │ IDENTI_DEPORTISTA (FK)   │
              │ NIT_ENTIDAD (FK)         │
              └──────────────────────────┘

┌──────────────────────┐     ┌──────────────────────────┐
│   Somatotipo         │     │  SomatotipoDetalle        │
│──────────────────────│     │──────────────────────────│
│ id_Somatotipo (PK)   │1  * │ ID (PK)                  │
│ FECHA_MEDIDA         │────►│ id_Somatotipo (FK)       │
│ IDENTI_DEPORTISTA(FK)│     │ ESTA_USER_CM             │
│ LOGIN_USER           │     │ PESO_kg                  │
│ OBSERV               │     │ PLIEGUE_TRICIPITAL       │
│ UNIQUE(deportista,   │     │ PLIEGUE_SUBESCAPULAR     │
│       fecha)         │     │ PLIEGUE_SUPRAILIACO      │
└──────────────────────┘     │ PLIEGUE_ABDOMINAL        │
                             │ PLIEGUE_MUSLO_ANT        │
                             │ PLIEGUE_MEDIAL_PIERNA    │
                             │ DIAMETRO_BIEPI_MUNECA    │
                             │ DIAMETRO_BIEPI_FEMUR     │
                             │ DIAMETRO_CODO            │
                             │ PERIMETRO_BICED_CONTRAIDO│
                             │ PERIMETRO_PIERNA         │
                             │ CIRCUNFERENCIA_CARPO     │
                             └──────────────────────────┘

┌──────────────────────────────────────┐
│  CDRVistaValoracionCorporal (VIEW)   │
│──────────────────────────────────────│
│ id_Somatotipo, FECHA_MEDIDA,         │
│ IDENTI_DEPORTISTA, NOMBRE_DEPORTISTA │
│ + todas las mediciones               │
│ + EDAD, SEXO_DEPORTISTA              │
│ + PorcGrasoJonson, PorcGrasoFaulker, │
│   PorcRasoYuasz                      │
│ + PesoGrasoJhonston, PesoRasoFaulker,│
│   PesoRasoYuazs                      │
│ + PesoOseo, PesoResidual, Mma        │
│ + IMC, EstadoIMC                     │
│ + Complexion, TipoComplexion         │
│ + Endomorfismo, Mesomorfismo,        │
│   Ectomorfismo                       │
│ + EscalaEndomorfismo,                │
│   EscalaMesomorfismo,                │
│   EscalaEctomorfismo                 │
│ + X, Y                               │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  CDRTablaAuditoria                   │
│──────────────────────────────────────│
│ ID_AUDIT (PK)                        │
│ OCCURRED_AT_UTC                      │
│ ACTOR_USER_ID, ACTOR_LOGIN           │
│ ACTION_CODE                          │
│ RESOURCE_TYPE, RESOURCE_ID           │
│ EVENT_RESULT                         │
│ HTTP_METHOD, ENDPOINT, STATUS_CODE   │
│ CLIENT_IP, USER_AGENT                │
│ CORRELATION_ID                       │
│ REQUEST_JSON, RESPONSE_JSON          │
│ ERROR_MESSAGE                        │
└──────────────────────────────────────┘
```

### 9.2 Relaciones

- Un **Usuario** tiene un **TipoUser**.
- Un **Deportista** tiene un **TipoDocumento**, un **Estrato**, un **NivelEducativo**.
- Un **DeporteDeportista** (asignación) relaciona un **Deportista**, un **Deporte** y una **Entidad**.
- Un **Somatotipo** pertenece a un **Deportista** y tiene uno o más **SomatotipoDetalle**.
- La vista **CDRVistaValoracionCorporal** calcula indicadores a partir de Somatotipo + SomatotipoDetalle + Deportista.
- La tabla **Auditoria** registra operaciones del sistema.

---

## 10. Data Requirements

### 10.1 Datos de deportistas

| Campo | Tipo | Obligatorio | Validación |
|-------|------|-------------|------------|
| IDENTI_DEPORTISTA | String(20) | Sí | Mínimo 1 carácter |
| TIPO_IDENTI | Integer | Sí | FK a CDRTablaTipoDocumento |
| NOMBRE_DEPORTISTA | String(50) | Sí | Mínimo 1 carácter |
| SEXO_DEPORTISTA | String(1) | Sí | M o F |
| FECHA_NAC | Date | No | No futura |
| E_MAIL | String(50) | No | Formato email válido |

### 10.2 Datos de valoración (14 campos de medición)

| Campo | Unidad | Rango |
|-------|--------|-------|
| ESTA_USER_CM | cm | >50 y ≤250 |
| PESO_kg | kg | >10 y ≤300 |
| PLIEGUE_TRICIPITAL | mm | >0 y ≤100 |
| PLIEGUE_SUBESCAPULAR | mm | >0 y ≤100 |
| PLIEGUE_SUPRAILIACO | mm | >0 y ≤100 |
| PLIEGUE_ABDOMINAL | mm | >0 y ≤100 |
| PLIEGUE_MUSLO_ANT | mm | >0 y ≤100 |
| PLIEGUE_MEDIAL_PIERNA | mm | >0 y ≤100 |
| DIAMETRO_BIEPI_MUNECA | mm | >0 y ≤200 |
| DIAMETRO_BIEPI_FEMUR | mm | >0 y ≤200 |
| DIAMETRO_CODO | mm | >0 y ≤200 |
| PERIMETRO_BICED_CONTRAIDO | mm | >0 y ≤250 |
| PERIMETRO_PIERNA | mm | >0 y ≤250 |
| CIRCUNFERENCIA_CARPO | mm | >0 y ≤200 |

### 10.3 Datos calculados (vista SQL)

| Campo | Descripción |
|-------|-------------|
| IMC | Índice de masa corporal (peso/estatura²) |
| EstadoIMC | Clasificación textual del IMC |
| PorcGrasoJonson | % grasa método Johnston |
| PorcGrasoFaulker | % grasa método Faulkner |
| PorcRasoYuasz | % masa rasa método Yuhasz |
| PesoOseo | Masa ósea estimada |
| PesoResidual | Masa residual estimada |
| Mma | Masa muscular activa |
| Endomorfismo | Componente endomórfico |
| Mesomorfismo | Componente mesomórfico |
| Ectomorfismo | Componente ectomórfico |
| X, Y | Coordenadas de somatocarta |
| Complexion | Índice de complexión |
| TipoComplexion | Clasificación textual de complexión |

---

## 11. Business Rules

| ID | Regla |
|----|-------|
| BR-001 | Una valoración pertenece a un único deportista. |
| BR-002 | Un deportista puede tener múltiples valoraciones en diferentes fechas. |
| BR-003 | No puede haber dos valoraciones del mismo deportista en la misma fecha (constraint único). |
| BR-004 | Una valoración debe tener al menos una toma de medición (detalle). |
| BR-005 | El análisis longitudinal requiere mínimo dos valoraciones. |
| BR-006 | El análisis individual corresponde a una valoración puntual. |
| BR-007 | Las asignaciones relacionan deportistas con entidades y deportes. |
| BR-008 | Los datos antropométricos deben ser positivos y estar dentro de rangos plausibles. |
| BR-009 | La generación de PDF depende de una valoración existente con sus detalles. |
| BR-010 | El sexo del deportista debe ser M o F. |
| BR-011 | La fecha de nacimiento no puede estar en el futuro. |
| BR-012 | La fecha de medición no puede estar en el futuro. |
| BR-013 | El NIT de entidad debe ser único. |
| BR-014 | El email, si se proporciona, debe tener formato válido. |

---

## 12. UX Requirements

| ID | Requisito |
|----|-----------|
| UX-001 | Dashboard con saludo personalizado y métricas clave. |
| UX-002 | Navegación lateral (sidebar) en escritorio, menú hamburguesa en móvil. |
| UX-003 | Historial de rutas compatible con navegación atrás en Android y navegador. |
| UX-004 | Tarjetas de módulo con iconos Material vectoriales uniformes. |
| UX-005 | Estados vacíos con mensajes informativos y acción sugerida. |
| UX-006 | Formularios con validación en tiempo real. |
| UX-007 | Confirmación modal antes de operaciones destructivas. |
| UX-008 | Notificaciones tipo SnackBar para operaciones exitosas y errores. |
| UX-009 | Historial con layout master-detail adaptativo. |
| UX-010 | Diferenciación visual clara entre análisis individual y longitudinal. |
| UX-011 | Unidades de medida visibles en todos los campos y reportes. |
| UX-012 | Diseño responsive sin scroll horizontal no deseado. |
| UX-013 | Web y Android pueden compartir lógica y datos, pero deben usar composiciones visuales independientes cuando el flujo móvil lo requiera. |
| UX-014 | Deportistas móvil usa un flujo de cuatro pasos; deportes, entidades y asignaciones usan tarjetas y formularios separados. |
| UX-015 | El login permite mostrar/ocultar contraseña y el encabezado móvil permite cerrar sesión. |
| UX-016 | El análisis longitudinal móvil conserva todos los datos funcionales del panel Web en secciones adaptadas. |

---

## 13. Reporting Requirements

### 13.1 PDF individual de valoración

**Contenido mínimo:**

- Datos del deportista (nombre, ID, edad, sexo).
- Fecha de medición.
- Usuario que registró.
- Tabla de mediciones antropométricas (14 campos).
- Composición corporal con Yuhasz como método principal, Faulkner como comparación y masas corporales.
- IMC y estado.
- Complexión física.
- Componentes de somatotipo con escalas descriptivas.
- Somatocarta con ubicación del deportista.
- Gráfico de distribución de masas.

### 13.2 PDF longitudinal

**Contenido mínimo:**

- Datos del deportista.
- Tabla histórica de todas las valoraciones.
- Gráficos de tendencia para variables principales.
- Somatocarta longitudinal con trayectoria.
- Tarjetas de cambio (valor inicial, final, delta, %).

### 13.3 Reglas de generación

- Los PDFs se generan íntegramente en el backend sin dependencias externas de PDF.
- El PDF debe ser válido (iniciar con firma `%PDF`).
- Las imágenes PNG se decodifican internamente con soporte para filtro Paeth.
- En Web, el PDF se entrega al navegador; en escritorio se abre externamente; en Android se puede compartir mediante `ACTION_SEND` con URI `content://` proporcionado por `FileProvider`.

---

## 14. Testing Requirements

| Categoría | Descripción |
|-----------|-------------|
| Unitarias | Helpers de frontend (formatters, form_helpers, interpretation). |
| Componentes | Componentes UI, table_builders, somatocarta, composition_analysis. |
| Integración | Servicios backend con SQLite temporal. |
| API | Endpoints con autenticación, validación y errores. |
| Esquemas | Validación Pydantic de entradas. |
| PDF | Generación de PDFs válidos. |
| Contrato de vista | Validación de columnas de CDRVistaValoracionCorporal. |
| Navegación | Flujo entre pantallas. |
| Longitudinal | Análisis temporal y gráficos. |
| Valoración | Vista de captura de mediciones. |
| Negativas | Credenciales inválidas, campos vacíos, rangos fuera, duplicados. |

**Resultado actual:** 227 tests y 7 subpruebas pasando.

---

## 15. Acceptance Criteria

### Autenticación

- [ ] Login con credenciales válidas retorna token JWT.
- [ ] Login con credenciales inválidas retorna 401.
- [ ] Endpoints protegidos sin token retornan 401.

### Deportistas

- [ ] Se puede crear, listar, buscar, editar y eliminar un deportista.
- [ ] Campos obligatorios vacíos retornan error 422.
- [ ] ID duplicado retorna error 400.

### Valoraciones

- [ ] Se puede crear una valoración con múltiples tomas.
- [ ] Valores fuera de rango retornan error 422.
- [ ] Fecha duplicada por deportista retorna error.
- [ ] Fecha futura retorna error 422.

### Análisis

- [ ] El historial muestra todos los indicadores calculados.
- [ ] La somatocarta ubica correctamente al deportista.
- [ ] El análisis longitudinal requiere mínimo 2 valoraciones.

### PDFs

- [x] PDF individual se descarga, contiene datos variables y es válido.
- [x] PDF longitudinal se descarga, contiene la serie histórica y es válido.

### Responsive

- [ ] La interfaz se adapta a móvil, tablet y escritorio.

---

## 16. Open Questions

| ID | Pregunta | Estado |
|----|----------|--------|
| OQ-001 | ¿Están clínicamente validadas las fórmulas de la vista SQL? | Pendiente de validar con profesional. |
| OQ-002 | ¿Por qué el mesomorfismo resultaba negativo para atletas musculares? | Resuelto en migración 004: diámetros históricos en cm y perímetros sin corrección por pliegues. |
| OQ-003 | ¿Por qué el peso óseo resultaba 0.35-0.50 kg? | Resuelto en migración 004: diámetros históricos almacenados en cm pero interpretados como mm. |
| OQ-004 | ¿Se requiere módulo de categorías de peso para deportes como boxeo? | Pendiente de definir con usuarios. |
| OQ-005 | ¿Se implementará control de roles y permisos granulares? | Pendiente de definir. |
| OQ-006 | ¿Se migrarán las contraseñas a hash seguro? | Pendiente de planificar. |
| OQ-007 | ¿Cuál es la definición SQL completa de CDRVistaValoracionCorporal? | Se puede obtener con `scripts/inspect_somatotipo_view.py`. |

---

## 17. Future Work

### Corto plazo

- Ejecutar campaña visual responsive en móvil, tablet y escritorio.
- Ejecutar validación visual responsive en dispositivos reales.
- Definir política CORS por ambiente.
- Aprobar metodológicamente el protocolo antropométrico con ciencias del deporte.

### Mediano plazo

- Agregar módulo de categorías de peso deportivas.
- Implementar migraciones con Alembic.
- Agregar control de roles y permisos.
- Exportación CSV/Excel de historial.
- Filtros por rango de fechas en análisis longitudinal.

### Trabajo resuelto el 21 de junio de 2026

- Fórmulas de somatotipo, grasa, masa ósea, residual y muscular corregidas mediante migración `004`.
- Unidades históricas normalizadas; 76 valoraciones MySQL verificadas sin diferencias.
- Restricciones únicas e integridad referencial aplicadas mediante migraciones `002` y `003`.
- Confirmaciones de eliminación incorporadas en las pantallas correspondientes.
- Texto de ectomorfismo corregido.

### Largo plazo

- Recomendaciones personalizadas basadas en perfil antropométrico.
- Objetivos deportivos y seguimiento de metas.
- Validación SUS (System Usability Scale) con usuarios reales.
- Análisis comparativo por deporte y entidad.
- Diseño pretest-postest para estudios de intervención.
- Modo oscuro.
- Plantillas de informes configurables.

---

*Documento generado bajo enfoque SDD — Spec-Driven Development.*
*Fusionado con `especificacion_sdd_somatocarta.md` el 15 de junio de 2026.*

---

# Apéndices — Contenido técnico detallado

Los siguientes apéndices incorporan contenido de la especificación SDD original que complementa las secciones anteriores con contratos API, flujos, diseño de interfaz, seguridad, evaluación arquitectónica y decisiones de diseño.

---

## Apéndice A: Contratos API completos

### A.1 Autenticación

#### `POST /auth/login`

Payload:

```json
{
  "username": "usuario",
  "password": "clave"
}
```

Respuesta:

```json
{
  "access_token": "jwt",
  "token_type": "bearer",
  "username": "Nombre Usuario",
  "login_user": "usuario",
  "user_id": 1
}
```

### A.2 Deportistas

#### `GET /deportistas/`

Parámetros: `search`, `page`, `page_size`

Respuesta:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 50
}
```

#### `GET /deportistas/{identi}`

Obtiene un deportista por identificación.

#### `POST /deportistas/`

Crea un deportista.

#### `PUT /deportistas/{identi}`

Actualiza un deportista.

#### `DELETE /deportistas/{identi}`

Elimina un deportista.

### A.3 Entidades

#### `GET /entidades/`

Parámetros: `search`, `page`, `page_size`

#### `POST /entidades/`

Crea una entidad. Payload: NIT_ENTIDAD, RAZON_SOCIAL, TELEFONO, CONTACTO, E_MAIL.

#### `PUT /entidades/{nit}`

Actualiza una entidad.

#### `DELETE /entidades/{nit}`

Elimina una entidad.

### A.4 Deportes

#### `GET /deportes/`

Parámetros: `search`, `page`, `page_size`

#### `POST /deportes/`

Crea un deporte. Payload: DEPORTE, ID_DEPORTE (opcional).

#### `PUT /deportes/{deporte_id}`

Actualiza un deporte.

#### `DELETE /deportes/{deporte_id}`

Elimina un deporte.

### A.5 Asignaciones

#### `GET /asignaciones/`

Parámetros: `search`, `page`, `page_size`

Cada elemento conserva `id`, `ID_DEPORTE`, `IDENTI_DEPORTISTA` y `NIT_ENTIDAD`, y puede incluir `NOMBRE_DEPORTISTA`, `DEPORTE` y `RAZON_SOCIAL` para presentación.

#### `POST /asignaciones/`

Crea una asignación. Payload: ID_DEPORTE, IDENTI_DEPORTISTA, NIT_ENTIDAD.

#### `PUT /asignaciones/{assignment_id}`

Actualiza una asignación.

#### `DELETE /asignaciones/{assignment_id}`

Elimina una asignación.

### A.6 Somatotipo y valoración corporal

#### `POST /somatotipo/`

Crea una valoración nueva con encabezado y detalles.

Payload:

```json
{
  "IDENTI_DEPORTISTA": "1001",
  "LOGIN_USER": "admin",
  "FECHA_MEDIDA": "2026-06-08",
  "OBSERV": "Control",
  "DETALLES": [
    {
      "ESTA_USER_CM": 170,
      "PESO_kg": 65,
      "PLIEGUE_TRICIPITAL": 10,
      "PLIEGUE_SUBESCAPULAR": 9,
      "PLIEGUE_SUPRAILIACO": 11,
      "PLIEGUE_ABDOMINAL": 16,
      "PLIEGUE_MUSLO_ANT": 7,
      "PLIEGUE_MEDIAL_PIERNA": 9,
      "DIAMETRO_BIEPI_MUNECA": 55,
      "DIAMETRO_BIEPI_FEMUR": 88,
      "DIAMETRO_CODO": 66,
      "PERIMETRO_BICED_CONTRAIDO": 34.2,
      "PERIMETRO_PIERNA": 52,
      "CIRCUNFERENCIA_CARPO": 20.5
    }
  ]
}
```

#### `GET /somatotipo/deportista/{identi}`

Obtiene historial desde tablas base.

#### `GET /somatotipo/vista/deportista/{identi}`

Obtiene historial calculado desde la vista SQL. Parámetros: `page`, `page_size`.

#### `GET /somatotipo/editable/deportista/{identi}`

Lista valoraciones almacenadas con detalles editables.

#### `GET /somatotipo/editable/{id_somatotipo}`

Carga una valoración completa editable.

#### `POST /somatotipo/{id_somatotipo}/detalle`

Agrega una nueva toma/medición al detalle de una valoración existente.

#### `PUT /somatotipo/detalle/{detalle_id}`

Actualiza una medición específica ya almacenada.

#### `DELETE /somatotipo/detalle/{detalle_id}`

Elimina una toma/medición específica sin eliminar la valoración principal.

#### `DELETE /somatotipo/{id_somatotipo}`

Elimina una valoración completa y sus detalles.

#### `GET /somatotipo/{id_somatotipo}/pdf`

Genera PDF individual de valoración.

#### `GET /somatotipo/vista/deportista/{identi}/longitudinal/pdf`

Genera PDF longitudinal.

#### `GET /somatotipo/vista/contrato`

Valida que la vista `CDRVistaValoracionCorporal` exponga las columnas esperadas.

### A.7 Catálogos

- `GET /catalogos/tipos_documento`
- `GET /catalogos/estratos`
- `GET /catalogos/niveles_educativos`

### A.8 Archivos

#### `POST /files/upload`

Sube imágenes JPG o PNG. Restricciones: extensiones `.jpg`, `.jpeg`, `.png`; content types `image/jpeg`, `image/png`; tamaño máximo 5 MB.

### A.9 Dashboard

#### `GET /dashboard/summary`

Devuelve métricas operativas y contrato de vista SQL.

### A.10 Salud

- `GET /` — Health check básico.
- `GET /health` — Verificación de conexión a base de datos.

---

## Apéndice B: Flujos principales paso a paso

### B.1 Crear valoración nueva

1. Usuario inicia sesión.
2. Entra a `Valoración Corporal`.
3. Busca deportista.
4. Captura mediciones.
5. Agrega medición a la lista.
6. Guarda valoración.
7. Backend crea encabezado en `CDRTablaSomatotipo`.
8. Backend crea uno o varios detalles en tabla de detalle.
9. Historial consulta resultados desde `CDRVistaValoracionCorporal`.

### B.2 Editar valoración almacenada

1. Usuario busca deportista en `Valoración Corporal`.
2. La app lista `Valoraciones almacenadas`.
3. Usuario pulsa `Cargar`.
4. La app carga detalles con `ID`.
5. Usuario selecciona editar una medición.
6. El formulario se llena con los datos de esa medición.
7. Usuario pulsa `Actualizar Medición`.
8. Frontend llama `PUT /somatotipo/detalle/{detalle_id}`.
9. Backend actualiza solo ese detalle y hace `commit`.
10. La vista SQL recalcula resultados cuando se consulte de nuevo.

### B.3 Eliminar valoración almacenada

1. Usuario busca deportista.
2. Selecciona una valoración almacenada.
3. Pulsa `Eliminar`.
4. Frontend llama `DELETE /somatotipo/{id_somatotipo}`.
5. Backend elimina detalles asociados.
6. Backend elimina encabezado.
7. Frontend refresca lista y limpia selección si corresponde.

### B.4 Consultar historial y descargar PDF

1. Usuario entra a `Historial`.
2. Busca deportista.
3. Backend retorna registros paginados desde `CDRVistaValoracionCorporal`.
4. Frontend agrupa registros por `id_Somatotipo`.
5. Usuario abre detalle.
6. Usuario revisa medidas, composición, análisis, somatotipo y somatocarta.
7. Usuario descarga PDF individual.

### B.5 Análisis longitudinal

1. Usuario busca deportista en historial.
2. Frontend conserva todas las valoraciones encontradas.
3. Usuario pulsa `Ver análisis`.
4. La app muestra tarjetas, gráfico temporal y somatocarta longitudinal.
5. Usuario puede descargar PDF longitudinal.

---

## Apéndice C: Diseño de interfaz

### C.1 Principios

- Diseño basado en tarjetas.
- Uso consistente de color primario azul.
- Grillas responsivas con `ResponsiveRow`.
- Imágenes de referencia integradas en análisis.
- Evitar doble scroll en pantallas críticas.
- Mantener legibilidad de imágenes con contenedores adaptativos y desplazamiento horizontal cuando es necesario.

### C.2 Orden de información en detalle de valoración

1. Medidas.
2. Composición:
   - comparación de métodos de grasa;
   - distribución corporal;
   - gráfico de pastel de masas corporales.
3. Análisis:
   - análisis IMC con imagen;
   - complexión física con imagen.
4. Somatotipo:
   - imagen de somatotipos corporales;
   - componentes y clasificación;
   - somatocarta.

### C.3 Diseño adaptativo

- **Celular:** navegación por pantalla única; lista o detalle, no ambos al mismo tiempo; CRUD mediante tarjetas/formularios móviles; análisis longitudinal completo en secciones verticales; tablas e imágenes con scroll horizontal cuando no quepan.
- **Tableta:** grillas de dos columnas cuando el ancho lo permita; tarjetas apilables.
- **Laptop/escritorio:** layout master-detail; mayor densidad de información; tablas y gráficos visibles simultáneamente.

---

## Apéndice D: Seguridad detallada

### D.1 Estado actual

- Las rutas privadas dependen de `get_current_user`.
- El token JWT se decodifica con `python-jose`.
- El token incluye `sub` y `id`.
- El frontend envía token mediante `Authorization: Bearer`.
- La carga de imágenes valida extensión, tipo MIME y tamaño máximo.
- Android comparte PDF mediante `FileProvider`, permiso temporal de lectura y MIME `application/pdf`; no expone rutas privadas directas.

### D.2 Riesgos detectados

- La autenticación compara contraseña en texto plano según compatibilidad con la base heredada.
- `SECRET_KEY` tiene valor por defecto si no se define en `.env`.
- No hay control granular de roles por módulo.
- No se observa control explícito de CORS.

### D.3 Recomendaciones de seguridad

- Migrar contraseñas a hash seguro.
- Obligar `SECRET_KEY` por variable de entorno en ambientes productivos.
- Agregar roles y permisos.
- Registrar auditoría de creación, edición, eliminación con usuario responsable, fecha/hora y valores antes/después.
- Agregar confirmación explícita en UI antes de eliminación definitiva.

---

## Apéndice E: Evaluación arquitectónica

### E.1 Fortalezas

- Separación razonable entre frontend, backend, servicios y modelos.
- `ApiClient` centraliza comunicación HTTP.
- Routers delegan lógica transaccional a servicios.
- Uso de schemas Pydantic para validar entradas.
- Suite de pruebas amplia para el tamaño actual de la app (227 tests y 7 subpruebas).
- Diseño visual más coherente y adaptativo que versiones previas.
- Cálculos derivados desacoplados del frontend.
- PDFs integrados sin dependencia externa pesada.

### E.2 Debilidades

- La vista SQL es una dependencia crítica y opaca para los cálculos.
- Los nombres técnicos de columnas tienen errores históricos que afectan mantenibilidad.
- No hay migraciones de base de datos.
- Los PDFs se construyen manualmente, lo que aumenta complejidad de mantenimiento.
- Falta confirmación modal robusta para operaciones destructivas.

### E.3 Riesgos técnicos

- Si cambia `CDRVistaValoracionCorporal`, historial, PDFs y análisis pueden fallar.
- Si la vista retorna múltiples filas con el mismo `id_Somatotipo`, SQLAlchemy puede deduplicar por clave primaria mapeada.
- Si los cálculos SQL no están clínicamente validados, la app puede mostrar resultados incorrectos aunque el código funcione.
- Si la red o backend no están activos, la app de escritorio pierde funcionalidad principal.

---

## Apéndice F: Decisiones de diseño vigentes

- Mantener cálculos en la vista SQL.
- Mantener nombres técnicos de columnas para compatibilidad.
- Corregir etiquetas visibles al usuario sin renombrar columnas reales.
- Mantener campos Johnston únicamente por compatibilidad y no mostrarlos como referencia clínica.
- Usar masa grasa Yuhasz en el balance de masas.
- Usar Flet como capa visual multiplataforma.
- Usar FastAPI como API local/remota.
- Usar MySQL como base productiva.
- Usar SQLite solo para pruebas de integración de servicios.
