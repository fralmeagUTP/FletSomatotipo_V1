# Especificación de Diseño de Software - Somatocarta

## 1. Propósito del documento

Este documento consolida la especificación técnica y funcional de la aplicación Somatocarta en su estado actual. Está escrito como un SDD (Software Design Document) para servir como referencia de arquitectura, alcance implementado, contratos técnicos, riesgos y próximos pasos de evolución.

## 2. Resumen ejecutivo

Somatocarta es una aplicación de escritorio/web construida con Flet en el frontend y FastAPI en el backend. Su objetivo es gestionar deportistas, registrar valoraciones antropométricas, consultar resultados calculados desde una vista SQL, visualizar análisis corporal y generar informes PDF.

La solución actual se organiza en dos capas principales:

- Frontend Flet: pantallas, navegación, componentes visuales, gráficos e interacción con usuario.
- Backend FastAPI: autenticación, API REST, persistencia SQLAlchemy, servicios de dominio, generación de PDF y validaciones.

La base de datos conserva la responsabilidad de los cálculos derivados por medio de la vista `CDRVistaValoracionCorporal`. La aplicación Python captura datos base, persiste mediciones y consume los resultados calculados desde esa vista.

## 3. Alcance funcional actual

### 3.1. Autenticación

- Inicio de sesión con usuario y contraseña.
- Generación de token JWT.
- Protección de rutas privadas mediante `Authorization: Bearer`.
- Conservación de sesión en Flet con `access_token`, `username`, `login_user` y `user_id`.

### 3.2. Dashboard

- Panel principal con acceso a módulos.
- Métricas operativas:
  - total de deportistas;
  - total de valoraciones;
  - estado del contrato de la vista SQL.
- Uso de imagen gráfica desde `assets/`.

### 3.3. Gestión de deportistas

- Listado paginado.
- Búsqueda por nombre o identificación.
- Creación de deportistas.
- Edición de datos personales, demográficos, contacto e institución.
- Eliminación de deportistas.
- Carga de fotografía con validación de imagen JPG/PNG.
- Uso de catálogos:
  - tipos de documento;
  - estratos;
  - niveles educativos.

### 3.4. Valoración corporal

- Búsqueda y selección de deportista.
- Captura de datos básicos:
  - fecha de medición;
  - estatura;
  - peso.
- Captura de pliegues cutáneos:
  - tricipital;
  - subescapular;
  - suprailiaco;
  - abdominal;
  - muslo anterior;
  - pierna medial.
- Captura de diámetros y perímetros:
  - muñeca;
  - fémur;
  - codo;
  - carpo;
  - bíceps contraído;
  - pierna.
- Agregar mediciones a una lista local antes de guardar.
- Editar y eliminar mediciones locales antes de persistir.
- Guardar valoración nueva con encabezado y detalles.
- Buscar valoraciones almacenadas del deportista.
- Cargar una valoración almacenada.
- Editar una medición específica ya almacenada.
- Actualizar una medición persistida mediante `PUT /somatotipo/detalle/{detalle_id}`.
- Eliminar una valoración completa mediante `DELETE /somatotipo/{id_somatotipo}`.

### 3.5. Historial corporal

- Búsqueda de deportista por nombre o identificación.
- Listado paginado de valoraciones corporales.
- Visualización de detalle por valoración.
- Diseño master-detail adaptativo:
  - escritorio: lista y detalle simultáneos;
  - móvil/tablet: alternancia entre lista y detalle para evitar navegación confusa.
- Descarga de informe PDF de una valoración individual.
- Eliminación de valoración desde historial.

### 3.6. Análisis de resultados

La app muestra resultados calculados desde `CDRVistaValoracionCorporal`:

- IMC y estado IMC.
- Complexión física.
- Porcentaje graso por métodos:
  - Yuhasz;
  - Faulkner;
  - Johnston.
- Masa grasa por métodos:
  - Yuhasz;
  - Faulkner;
  - Johnston.
- Masa ósea.
- Masa residual.
- Masa muscular.
- Endomorfismo.
- Mesomorfismo.
- Ectomorfismo.
- Coordenadas de somatocarta `X` y `Y`.

### 3.7. Composición corporal

- Comparación de métodos de grasa.
- Tabla de distribución del peso corporal.
- Validación de coherencia:
  - `Peso corporal = masa grasa Johnston + masa muscular + masa ósea + masa residual`.
- Alerta si la diferencia supera el umbral configurado.
- Gráfico de pastel para distribución de masas corporales.

### 3.8. Somatocarta

- Uso de imagen de referencia `Somatocarta.png`.
- Ubicación del punto del deportista usando coordenadas `X` y `Y`.
- Calibración del gráfico por interpolación de marcas reales de los ejes.
- Visualización de etiqueta del deportista.
- Badge con coordenadas.
- Diseño con desplazamiento horizontal para preservar legibilidad en pantallas pequeñas.

### 3.9. Análisis longitudinal

- Comparación temporal de valoraciones de un deportista.
- Variables graficables:
  - peso;
  - IMC;
  - porcentaje graso Yuhasz;
  - porcentaje graso Faulkner;
  - masa muscular;
  - endomorfismo;
  - mesomorfismo;
  - ectomorfismo.
- Tarjetas de valor inicial, valor final, cambio absoluto y cambio porcentual.
- Gráfico de línea por variable.
- Somatocarta longitudinal con todos los puntos `X`, `Y` y fecha de medición.
- Informe PDF longitudinal.

### 3.10. Informes PDF

- PDF individual de valoración corporal.
- PDF longitudinal del deportista.
- Uso de la misma lógica visual y fuentes de datos del historial.
- Inclusión de:
  - datos del deportista;
  - métricas principales;
  - composición corporal;
  - mediciones antropométricas;
  - somatotipo;
  - somatocarta;
  - gráficos longitudinales cuando aplica.

## 4. Arquitectura de alto nivel

```text
Usuario
  |
  v
Frontend Flet
  - main.py
  - views/
  - src/frontend/
  |
  v
ApiClient HTTP
  |
  v
Backend FastAPI
  - routers/
  - schemas/
  - services/
  - models.py
  |
  v
Base de datos MySQL
  - tablas CDRTabla*
  - vista CDRVistaValoracionCorporal
```

## 5. Componentes principales

### 5.1. Entrada frontend

Archivo principal:

- `main.py`

Responsabilidades:

- inicializar aplicación Flet;
- configurar ventana;
- mostrar login;
- guardar sesión;
- redirigir a dashboard.

### 5.2. Vistas frontend

Directorio:

- `views/`

Vistas actuales:

- `dashboard.py`: inicio y métricas.
- `deportistas.py`: CRUD de deportistas.
- `valoracion.py`: captura, creación, carga, edición y eliminación de valoraciones.
- `historial.py`: historial, resultados, análisis y PDFs.

### 5.3. Utilidades frontend

Directorio:

- `src/frontend/`

Módulos relevantes:

- `api_client.py`: cliente único para consumir FastAPI.
- `navigation.py`: navegación centralizada.
- `theme.py`: colores, sombras y constantes visuales.
- `components.py`: componentes UI reutilizables.
- `form_helpers.py`: construcción de payloads.
- `table_builders.py`: filas y agrupación de tablas/listas.
- `assets.py`: rutas de imágenes de módulos y referencias.
- `somatocarta.py`: calibración y render de somatocarta.
- `composition_analysis.py`: análisis de composición corporal.
- `longitudinal_analysis.py`: análisis temporal y somatocarta longitudinal.
- `interpretation.py`: notas metodológicas e interpretación.
- `formatters.py`: formateo de valores.

### 5.4. Backend FastAPI

Archivo principal:

- `src/backend/main.py`

Responsabilidades:

- crear instancia FastAPI;
- montar archivos estáticos;
- registrar routers;
- exponer endpoints raíz y health check.

### 5.5. Routers backend

Directorio:

- `src/backend/routers/`

Routers:

- `auth.py`: autenticación.
- `deportistas.py`: CRUD de deportistas.
- `somatotipo.py`: valoraciones, historial, edición, PDFs y eliminación.
- `catalogos.py`: catálogos.
- `files.py`: carga de archivos.
- `dashboard.py`: métricas operativas.

### 5.6. Servicios backend

Directorio:

- `src/backend/services/`

Servicios:

- `deportistas_service.py`: operaciones de deportistas.
- `somatotipo_service.py`: creación, edición, historial, eliminación y PDFs de somatotipo.
- `pdf_service.py`: construcción manual de PDFs.
- `dashboard_service.py`: métricas de dashboard.
- `view_contract_service.py`: validación de columnas de la vista SQL.

### 5.7. Modelos y schemas

Modelos SQLAlchemy:

- `src/backend/models.py`

Schemas Pydantic:

- `src/backend/schemas/deportistas.py`
- `src/backend/schemas/somatotipo.py`

## 6. Modelo de datos

### 6.1. Tablas principales

#### `CDRTablaUsuarios`

Representa usuarios del sistema.

Campos relevantes:

- `ID_USER`
- `LOGIN_USER`
- `PSW_USER`
- `NOM_USER`
- `MAIL_USER`
- `ID_TIPO_USER`

#### `CDRTablaDeportistas`

Representa deportistas registrados.

Campos relevantes:

- `IDENTI_DEPORTISTA`
- `TIPO_IDENTI`
- `NOMBRE_DEPORTISTA`
- `FOTO_DEPORTISTA`
- `SEXO_DEPORTISTA`
- `FECHA_NAC`
- `CIUDAD_RESI`
- `E_MAIL`
- `NOMBRE_INSTITU`
- `OBSERVACIONES`

#### `CDRTablaSomatotipo`

Encabezado de valoración corporal.

Campos:

- `id_Somatotipo`
- `FECHA_MEDIDA`
- `IDENTI_DEPORTISTA`
- `LOGIN_USER`
- `OBSERV`

#### `CDRDetalleSomatotipo`

Detalle de mediciones antropométricas.

Campos:

- `ID`
- `id_Somatotipo`
- `ESTA_USER_CM`
- `PESO_kg`
- `PLIEGUE_TRICIPITAL`
- `PLIEGUE_SUBESCAPULAR`
- `PLIEGUE_SUPRAILIACO`
- `PLIEGUE_ABDOMINAL`
- `PLIEGUE_MUSLO_ANT`
- `PLIEGUE_MEDIAL_PIERNA`
- `DIAMETRO_BIEPI_MUNECA`
- `DIAMETRO_BIEPI_FEMUR`
- `DIAMETRO_CODO`
- `PERIMETRO_BICED_CONTRAIDO`
- `PERIMETRO_PIERNA`
- `CIRCUNFERENCIA_CARPO`

### 6.2. Vista SQL de resultados

#### `CDRVistaValoracionCorporal`

Es la fuente de verdad para cálculos derivados.

Campos consumidos:

- datos del deportista;
- mediciones base;
- composición corporal;
- masas corporales;
- IMC;
- complexión;
- componentes del somatotipo;
- escalas descriptivas;
- coordenadas `X` y `Y`.

Decisión actual:

- Los cálculos se mantienen en la vista SQL.
- La aplicación no recalcula fórmulas clínicas en Python.
- Al editar datos base, la vista SQL debe reflejar los resultados recalculados.

## 7. Contratos API

### 7.1. Autenticación

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

### 7.2. Deportistas

#### `GET /deportistas/`

Parámetros:

- `search`
- `page`
- `page_size`

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

### 7.3. Somatotipo y valoración corporal

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

Obtiene historial calculado desde la vista SQL.

Parámetros:

- `page`
- `page_size`

#### `GET /somatotipo/editable/deportista/{identi}`

Lista valoraciones almacenadas con detalles editables.

#### `GET /somatotipo/editable/{id_somatotipo}`

Carga una valoración completa editable.

#### `PUT /somatotipo/detalle/{detalle_id}`

Actualiza una medición específica ya almacenada.

#### `POST /somatotipo/{id_somatotipo}/detalle`

Agrega una nueva toma/medición al detalle de una valoración principal existente.

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

### 7.4. Catálogos

- `GET /catalogos/tipos_documento`
- `GET /catalogos/estratos`
- `GET /catalogos/niveles_educativos`

### 7.5. Archivos

#### `POST /files/upload`

Sube imágenes JPG o PNG.

Restricciones:

- extensiones permitidas: `.jpg`, `.jpeg`, `.png`;
- content types permitidos: `image/jpeg`, `image/png`;
- tamaño máximo: 5 MB.

### 7.6. Dashboard

#### `GET /dashboard/summary`

Devuelve métricas operativas y contrato de vista SQL.

## 8. Flujos principales

### 8.1. Crear valoración nueva

1. Usuario inicia sesión.
2. Entra a `Valoración Corporal`.
3. Busca deportista.
4. Captura mediciones.
5. Agrega medición a la lista.
6. Guarda valoración.
7. Backend crea encabezado en `CDRTablaSomatotipo`.
8. Backend crea uno o varios detalles en `CDRDetalleSomatotipo`.
9. Historial consulta resultados desde `CDRVistaValoracionCorporal`.

### 8.2. Editar valoración almacenada

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

### 8.3. Eliminar valoración almacenada

1. Usuario busca deportista.
2. Selecciona una valoración almacenada.
3. Pulsa `Eliminar`.
4. Frontend llama `DELETE /somatotipo/{id_somatotipo}`.
5. Backend elimina detalles asociados.
6. Backend elimina encabezado.
7. Frontend refresca lista y limpia selección si corresponde.

### 8.4. Consultar historial y descargar PDF

1. Usuario entra a `Historial`.
2. Busca deportista.
3. Backend retorna registros paginados desde `CDRVistaValoracionCorporal`.
4. Frontend agrupa registros por `id_Somatotipo`.
5. Usuario abre detalle.
6. Usuario revisa medidas, composición, análisis, somatotipo y somatocarta.
7. Usuario descarga PDF individual.

### 8.5. Análisis longitudinal

1. Usuario busca deportista en historial.
2. Frontend conserva todas las valoraciones encontradas.
3. Usuario pulsa `Ver análisis`.
4. La app muestra tarjetas, gráfico temporal y somatocarta longitudinal.
5. Usuario puede descargar PDF longitudinal.

## 9. Diseño de interfaz

### 9.1. Principios actuales

- Diseño basado en tarjetas.
- Uso consistente de color primario azul.
- Grillas responsivas con `ResponsiveRow`.
- Imágenes de referencia integradas en análisis.
- Evitar doble scroll en pantallas críticas.
- Mantener legibilidad de imágenes con contenedores adaptativos y desplazamiento horizontal cuando es necesario.

### 9.2. Orden de información en detalle de valoración

El detalle de historial se organiza así:

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

### 9.3. Diseño adaptativo

Comportamiento esperado:

- Celular:
  - navegación por pantalla única;
  - lista o detalle, no ambos al mismo tiempo;
  - tablas e imágenes con scroll horizontal cuando no quepan.
- Tableta:
  - grillas de dos columnas cuando el ancho lo permita;
  - tarjetas apilables.
- Laptop/escritorio:
  - layout master-detail;
  - mayor densidad de información;
  - tablas y gráficos visibles simultáneamente.

## 10. Reglas de validación

### 10.1. Deportista

- Identificación obligatoria, máximo 20 caracteres.
- Tipo de documento obligatorio.
- Nombre obligatorio, máximo 50 caracteres.
- Sexo permitido: `M` o `F`.
- Email validado si existe.
- Fecha de nacimiento no puede estar en el futuro.

### 10.2. Medición antropométrica

Rangos actuales:

- estatura: mayor a 50 y menor o igual a 250 cm;
- peso: mayor a 10 y menor o igual a 300 kg;
- pliegues: mayor a 0 y menor o igual a 100 mm;
- diámetros: mayor a 0 y menor o igual a 200 mm;
- perímetros: mayor a 0 y menor o igual a 250 cm;
- circunferencia carpo: mayor a 0 y menor o igual a 200.

### 10.3. Fecha de medición

- No puede estar en el futuro.

## 11. Seguridad

### 11.1. Estado actual

- Las rutas privadas dependen de `get_current_user`.
- El token JWT se decodifica con `python-jose`.
- El token incluye `sub` y `id`.
- El frontend envía token mediante `Authorization: Bearer`.
- La carga de imágenes valida extensión, tipo MIME y tamaño máximo.

### 11.2. Riesgos detectados

- La autenticación compara contraseña en texto plano según compatibilidad con la base heredada.
- `SECRET_KEY` tiene valor por defecto si no se define en `.env`.
- No hay control granular de roles por módulo.
- No hay auditoría de cambios para edición o eliminación de valoraciones.
- No se observa control explícito de CORS.

### 11.3. Recomendaciones de seguridad

- Migrar contraseñas a hash seguro.
- Obligar `SECRET_KEY` por variable de entorno en ambientes productivos.
- Agregar roles y permisos.
- Registrar auditoría de:
  - creación;
  - edición;
  - eliminación;
  - usuario responsable;
  - fecha/hora;
  - valores antes/después.
- Agregar confirmación explícita en UI antes de eliminación definitiva.

## 12. Calidad y pruebas

### 12.1. Suite actual

La suite cubre:

- seguridad básica de API;
- validaciones Pydantic;
- endpoints principales;
- servicios backend;
- integración SQLite;
- generación de PDF;
- contrato de vista SQL;
- cliente API frontend;
- componentes frontend;
- helpers de formularios;
- composición corporal;
- somatocarta;
- análisis longitudinal;
- vista de valoración corporal.

Resultado validado:

```text
126 passed
```

Comando:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### 12.2. Estrategia de pruebas recomendada

- Mantener pruebas unitarias para helpers de frontend.
- Mantener pruebas de integración con SQLite para servicios.
- Agregar pruebas contra MySQL real o contenedor para validar compatibilidad de vista SQL.
- Crear casos clínicos conocidos para validar fórmulas de la vista SQL.
- Agregar pruebas visuales o snapshots para layouts críticos.

## 13. Evaluación arquitectónica

### 13.1. Fortalezas

- Separación razonable entre frontend, backend, servicios y modelos.
- `ApiClient` centraliza comunicación HTTP.
- Routers delegan lógica transaccional a servicios.
- Uso de schemas Pydantic para validar entradas.
- Suite de pruebas amplia para el tamaño actual de la app.
- Diseño visual más coherente y adaptativo que versiones previas.
- Cálculos derivados desacoplados del frontend.
- PDFs integrados sin dependencia externa pesada.

### 13.2. Debilidades

- La vista SQL es una dependencia crítica y opaca para los cálculos.
- Los nombres técnicos de columnas tienen errores históricos que afectan mantenibilidad.
- No hay migraciones de base de datos.
- Los PDFs se construyen manualmente, lo que aumenta complejidad de mantenimiento.
- Hay textos con mojibake en algunos archivos y documentación existente; requiere limpieza sistemática de codificación.
- Falta auditoría de edición/eliminación.
- Falta confirmación modal robusta para operaciones destructivas.

### 13.3. Riesgos técnicos

- Si cambia `CDRVistaValoracionCorporal`, historial, PDFs y análisis pueden fallar.
- Si la vista retorna múltiples filas con el mismo `id_Somatotipo`, SQLAlchemy puede deduplicar por clave primaria mapeada.
- Si los cálculos SQL no están clínicamente validados, la app puede mostrar resultados incorrectos aunque el código funcione.
- Si la red o backend no están activos, la app de escritorio pierde funcionalidad principal.

## 14. Decisiones de diseño vigentes

- Mantener cálculos en la vista SQL.
- Mantener nombres técnicos de columnas para compatibilidad.
- Corregir etiquetas visibles al usuario sin renombrar columnas reales.
- Usar `Johnston` como etiqueta visible para el método previamente confundido como Jackson/Pollock.
- Usar masa grasa Johnston en el balance de masas.
- Usar Flet como capa visual multiplataforma.
- Usar FastAPI como API local/remota.
- Usar MySQL como base productiva.
- Usar SQLite solo para pruebas de integración de servicios.

## 15. Requisitos no funcionales

### 15.1. Portabilidad

La app debe poder ejecutarse en entornos compatibles con Python, Flet y FastAPI. La interfaz debe adaptarse a:

- celulares;
- tabletas;
- laptops;
- escritorio.

### 15.2. Rendimiento

Recomendaciones:

- Paginación en listados.
- Evitar consultas completas cuando solo se requiere una página.
- Mantener imágenes optimizadas.
- Evitar doble scroll en vistas principales.

### 15.3. Mantenibilidad

Recomendaciones:

- Mantener lógica de negocio en servicios.
- Mantener vistas sin llamadas directas a `requests`.
- Documentar cambios de la vista SQL.
- Evitar duplicación de tablas visuales y formateadores.

### 15.4. Usabilidad

Requisitos:

- Mensajes claros de error.
- Estados vacíos visibles.
- Unidades de medida en campos y reportes.
- Confirmación en acciones destructivas.
- Diseño adaptativo sin pérdida de contexto.

## 16. Backlog recomendado

### 16.1. Prioridad alta

- Limpiar codificación de textos visibles y documentación para eliminar caracteres raros.
- Agregar confirmación modal antes de eliminar valoraciones.
- Agregar auditoría de cambios en valoraciones.
- Validar clínicamente `CDRVistaValoracionCorporal`.
- Crear pruebas con datos antropométricos conocidos.

### 16.2. Prioridad media

- Agregar migraciones con Alembic.
- Agregar control de roles.
- Mejorar generación PDF con una capa declarativa de layout.
- Agregar exportación CSV/Excel de historial.
- Agregar filtros por rango de fechas en historial longitudinal.

### 16.3. Prioridad baja

- Agregar modo oscuro.
- Agregar configuración visual institucional.
- Agregar dashboard con tendencias agregadas.
- Agregar plantillas de informes configurables.

## 17. Criterios de aceptación del estado actual

La app se considera funcional en su estado actual si:

- El backend inicia correctamente.
- El frontend inicia correctamente.
- El usuario puede iniciar sesión.
- El dashboard muestra métricas.
- Se pueden listar, crear, editar y eliminar deportistas.
- Se puede crear una valoración nueva.
- Se puede buscar, cargar, editar y eliminar una valoración almacenada.
- El historial muestra resultados desde la vista SQL.
- La somatocarta ubica coordenadas `X`, `Y`.
- El análisis longitudinal grafica variables y somatocarta temporal.
- Los PDFs individual y longitudinal se descargan correctamente.
- La suite de pruebas pasa.

## 18. Conclusión

Somatocarta tiene una base arquitectónica funcional y suficientemente modular para seguir evolucionando. La separación entre vistas, cliente API, routers, servicios y modelos permite mantener el sistema con bajo acoplamiento relativo. El principal punto de atención es que la exactitud clínica depende de la vista SQL `CDRVistaValoracionCorporal`; por tanto, cualquier evaluación final del sistema debe incluir auditoría de esa vista y pruebas con casos clínicos conocidos.

El siguiente salto de calidad debe centrarse en seguridad, auditoría, limpieza de codificación, validación clínica y trazabilidad de cambios.
