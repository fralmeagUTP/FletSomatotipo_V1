# Valoracion Fisica Deportiva UTP - Spec-Driven Development

**Version:** 0.1
**Fecha:** 27 de junio de 2026
**Estado:** Propuesta tecnica
**Proyecto base:** Somatocarta v1.2.5 / SINVADE

---

## 1. Vision

### 1.1 Nombre del modulo

Valoracion Fisica Deportiva UTP.

### 1.2 Proposito

Digitalizar la prueba fisica aplicada a funcionarios, docentes, administrativos u otros integrantes de la Universidad Tecnologica de Pereira que representan a la institucion en algun deporte.

El modulo debe registrar los resultados de antropometria basica, fuerza, resistencia, flexibilidad y movilidad, asociarlos a un deportista existente y permitir consulta historica, analisis individual, seguimiento longitudinal e informes.

### 1.3 Relacion con Somatocarta

El nuevo producto se entrega como APK independiente al APK de Somatocarta/somatotipo. Comparte componentes funcionales y de datos del ecosistema actual, pero no debe aparecer como una simple pantalla adicional dentro del flujo principal de somatotipo.

El APK de Valoracion Fisica Deportiva reutiliza la arquitectura actual:

- Frontend Flet en `views/` y helpers en `src/frontend/`.
- Backend FastAPI en `src/backend/routers/`.
- Schemas Pydantic en `src/backend/schemas/`.
- Servicios transaccionales en `src/backend/services/`.
- Modelos SQLAlchemy en `src/backend/models.py`.
- Base de datos MySQL con InnoDB.
- Auditoria en `CDRTablaAuditoria` y `audit.log`.
- Integridad referencial con politica `RESTRICT`.

Pantallas compartidas permitidas:

- Login.
- Deportistas.
- Deportes.
- Asignaciones.

Pantallas propias del APK de Valoracion Fisica Deportiva:

- Inicio/dashboard del modulo deportivo.
- Registro de valoracion deportiva.
- Historial de valoraciones deportivas.
- Detalle/edicion de valoracion deportiva.
- Analisis individual deportivo.
- Analisis longitudinal deportivo.
- Reportes PDF deportivos.

El sujeto evaluado no se modela como funcionario independiente. Se registra en `CDRTablaDeportistas`, porque para el sistema actua como deportista representante de la UTP.

---

## 2. Problema

La valoracion fisica actual esta en formato Excel y funciona como ficha manual. Esto causa:

- Captura no estructurada de datos.
- Duplicidad potencial de pruebas por persona y fecha.
- Calculos manuales o inconsistentes.
- Dificultad para consultar historiales.
- Falta de integridad referencial con deportistas registrados.
- Falta de auditoria sobre creacion, edicion o eliminacion.
- Imposibilidad de generar reportes estandarizados desde la aplicacion.

---

## 3. Objetivos

| ID | Objetivo |
|----|----------|
| G-001 | Registrar una valoracion fisica asociada a `CDRTablaDeportistas`. |
| G-002 | Evitar duplicados por deportista y fecha de prueba. |
| G-003 | Calcular automaticamente IMC, masa grasa, masa libre de grasa y AKS. |
| G-004 | Registrar resultados de fuerza, resistencia, flexibilidad y movilidad. |
| G-005 | Permitir busqueda y consulta historica por deportista. |
| G-006 | Permitir edicion controlada de valoraciones existentes. |
| G-007 | Generar analisis individual de la valoracion fisica. |
| G-008 | Generar analisis longitudinal de pruebas fisicas. |
| G-009 | Generar informe PDF de valoracion fisica. |
| G-010 | Registrar auditoria de operaciones criticas. |
| G-011 | Mantener consistencia con la arquitectura y estilo visual de Somatocarta. |
| G-012 | Publicar Valoracion Fisica Deportiva como APK independiente que reutiliza login, deportistas, deportes y asignaciones. |

---

## 4. No Objetivos

| ID | No objetivo | Razon |
|----|-------------|-------|
| NG-001 | No reemplazar diagnostico medico. | La prueba es deportiva y funcional, no clinica. |
| NG-002 | No crear tabla separada de funcionarios. | Los funcionarios evaluados representan deportivamente a la UTP y se gestionan como deportistas. |
| NG-003 | No modificar `CDRTablaSomatotipo`. | La valoracion fisica es distinta a la valoracion antropometrica de somatotipo. |
| NG-004 | No calcular valoraciones textuales sin baremos oficiales. | Requieren tablas de referencia por sexo, edad y protocolo. |
| NG-005 | No prescribir entrenamiento automaticamente. | Fuera del alcance inicial. |
| NG-006 | No reemplazar la ficha profesional ni el criterio del evaluador. | El sistema captura, calcula y reporta. |
| NG-007 | No publicar Valoracion Fisica Deportiva como menu interno del APK de somatotipo. | Debe ser una aplicacion instalable independiente, aunque comparta pantallas y backend. |

---

## 5. Usuarios

### 5.1 Evaluador deportivo

Registra pruebas fisicas, valida datos, consulta resultados y genera informes.

### 5.2 Entrenador o delegado deportivo

Consulta la aptitud fisica y seguimiento del deportista que representa a la UTP.

### 5.3 Administrador

Gestiona usuarios, catastro de deportistas, deportes, entidades y auditoria.

### 5.4 Investigador

Consulta datos consolidados para analisis de poblacion deportiva universitaria.

### 5.5 Deportista representante

Sujeto evaluado. No necesariamente accede al sistema.

---

## 6. Historias de Usuario

```text
US-001: Como evaluador, quiero buscar un deportista por identificacion o nombre para asociarle una valoracion fisica.
US-002: Como evaluador, quiero registrar una nueva valoracion fisica con fecha de prueba.
US-003: Como evaluador, quiero capturar peso, talla, perimetro abdominal y porcentaje de grasa corporal.
US-004: Como evaluador, quiero que el sistema calcule IMC, masa grasa, masa libre de grasa y AKS.
US-005: Como evaluador, quiero registrar fuerza prensil derecha e izquierda, peso muerto y estabilidad core.
US-006: Como evaluador, quiero registrar datos del Test del Banco Queen College.
US-007: Como evaluador, quiero registrar flexibilidad sit and reach y movilidad FMS paso de valla.
US-008: Como evaluador, quiero guardar observaciones generales de la prueba.
US-009: Como evaluador, quiero evitar dos valoraciones del mismo deportista en la misma fecha.
US-010: Como evaluador, quiero editar una valoracion registrada si detecto un error.
US-011: Como evaluador, quiero eliminar una valoracion creada por error, con confirmacion.
US-012: Como entrenador, quiero consultar el historial de valoraciones fisicas de un deportista.
US-013: Como entrenador, quiero comparar indicadores fisicos a traves del tiempo.
US-014: Como usuario, quiero descargar un PDF con los resultados de la valoracion.
US-015: Como administrador, quiero que las operaciones queden auditadas.
```

---

## 7. Modelo de Dominio

### 7.1 Entidades principales

```text
CDRTablaDeportistas
    1 -> N
CDRTablaValoracionDeportiva
```

### 7.2 Tabla nueva

Tabla propuesta por la migracion:

```text
CDRTablaValoracionDeportiva
```

Clave primaria:

```text
ID_VALORACION_DEPORTIVA
```

Clave foranea:

```text
IDENTI_DEPORTISTA -> CDRTablaDeportistas.IDENTI_DEPORTISTA
```

Regla unica:

```text
UNIQUE (IDENTI_DEPORTISTA, FECHA_PRUEBA)
```

### 7.3 Campos capturados

Antropometria basica:

- `TALLA_M`
- `PESO_KG`
- `PERIMETRO_ABDOMINAL_CM`
- `PORC_GRASA_CORPORAL`
- Valoraciones textuales asociadas

Fuerza:

- `FUERZA_PRENSIL_D`
- `FUERZA_PRENSIL_I`
- `PESO_MUERTO_KG`
- `CORE_ANTERIOR_SEG`
- `CORE_POSTERIOR_SEG`
- Valoraciones textuales asociadas

Resistencia:

- `FC_REPOSO`
- `FC_MAXIMA`
- `FC_REC_15S`
- `FC_REC_1M`
- `FC_REC_3M`
- `VO2_MAX`
- `VO2_MAX_VALORACION`

Flexibilidad y movilidad:

- `FLEXIBILIDAD_PUNTUACION`
- `FLEXIBILIDAD_VALORACION`
- `MOVILIDAD_FMS_PUNTUACION`
- `MOVILIDAD_FMS_VALORACION`

### 7.4 Campos calculados en base de datos

```text
IMC = PESO_KG / TALLA_M^2
MASA_GRASA_KG = PESO_KG * PORC_GRASA_CORPORAL / 100
MASA_LIBRE_GRASA_KG = PESO_KG * (1 - PORC_GRASA_CORPORAL / 100)
AKS = MASA_LIBRE_GRASA_KG / TALLA_M^2
```

Estos campos son `GENERATED ALWAYS AS ... STORED` en MySQL.

---

## 8. Arquitectura Objetivo

### 8.0 Empaquetado APK

Valoracion Fisica Deportiva debe compilarse y distribuirse como APK independiente. Puede usar el mismo repositorio y componentes compartidos, pero debe tener punto de entrada, configuracion de navegacion, nombre visible, icono y flujo inicial propios.

APK de somatotipo:

- Mantiene sus pantallas actuales de somatotipo y valoracion corporal.
- No incorpora las pantallas propias de valoracion deportiva como opcion de menu obligatoria.

APK de Valoracion Fisica Deportiva:

- Inicia en login compartido.
- Despues de autenticacion, muestra el shell propio de valoracion deportiva.
- Reutiliza las pantallas compartidas de deportistas, deportes y asignaciones.
- Incluye solo las pantallas propias del modulo deportivo.

Componentes compartidos:

```text
views/login.py
views/deportistas.py
views/deportes.py
views/asignaciones.py
src/frontend/api_client.py
src/frontend/app_shell.py, si se parametriza por producto
src/frontend/navigation.py, si se parametriza por producto
```

Componentes especificos del APK deportivo:

```text
views/valoracion_deportiva.py
views/valoracion_deportiva_historial.py
views/valoracion_deportiva_analisis.py
views/valoracion_deportiva_longitudinal.py
src/frontend/valoracion_deportiva_helpers.py
```

### 8.1 Frontend

Archivos nuevos sugeridos:

```text
views/valoracion_deportiva.py
src/frontend/valoracion_deportiva_helpers.py
```

El modulo debe seguir el patron de `views/valoracion.py`:

- Busqueda de deportista.
- Formulario por secciones.
- Validacion visual de campos.
- Resumen antes de guardar.
- Confirmacion de creacion, edicion y eliminacion.
- Layout responsive para escritorio, tablet y movil.

### 8.2 Backend

Archivos nuevos sugeridos:

```text
src/backend/routers/valoracion_deportiva.py
src/backend/schemas/valoracion_deportiva.py
src/backend/services/valoracion_deportiva_service.py
```

Cambios en archivos existentes:

```text
src/backend/main.py
src/backend/models.py
src/frontend/api_client.py
src/frontend/navigation.py, parametrizado por producto/APK
src/frontend/app_shell.py, parametrizado por producto/APK
views/dashboard.py, solo si existe dashboard propio del APK deportivo
```

### 8.3 Base de datos

Migracion:

```text
scripts/migrations/005_prueba_fisica_representacion_utp.sql
```

Tabla:

```text
CDRTablaValoracionDeportiva
```

Motor:

```text
InnoDB
```

---

## 9. API Propuesta

Todas las rutas privadas requieren JWT mediante `Depends(get_current_user)`.

### 9.1 Crear valoracion

```http
POST /valoracion-deportiva/
```

Entrada:

```json
{
  "IDENTI_DEPORTISTA": "123",
  "FECHA_PRUEBA": "2026-06-27",
  "TALLA_M": 1.75,
  "PESO_KG": 80.0,
  "PERIMETRO_ABDOMINAL_CM": 88.0,
  "PORC_GRASA_CORPORAL": 20.0,
  "FUERZA_PRENSIL_D": 42.0,
  "FUERZA_PRENSIL_I": 40.0,
  "PESO_MUERTO_KG": 100.0,
  "CORE_ANTERIOR_SEG": 60.0,
  "CORE_POSTERIOR_SEG": 45.0,
  "FC_REPOSO": 70,
  "FC_MAXIMA": 168,
  "FC_REC_15S": 42,
  "FC_REC_1M": 120,
  "FC_REC_3M": 95,
  "VO2_MAX": 42.5,
  "FLEXIBILIDAD_PUNTUACION": 28.0,
  "MOVILIDAD_FMS_PUNTUACION": 2.0,
  "OBSERVACIONES": "Apto para representacion deportiva."
}
```

Salida:

```json
{
  "ID_VALORACION_DEPORTIVA": 1,
  "IDENTI_DEPORTISTA": "123",
  "FECHA_PRUEBA": "2026-06-27",
  "IMC": 26.12,
  "MASA_GRASA_KG": 16.0,
  "MASA_LIBRE_GRASA_KG": 64.0,
  "AKS": 20.9
}
```

### 9.2 Listar por deportista

```http
GET /valoracion-deportiva/deportista/{identi}
```

Debe devolver lista ordenada por `FECHA_PRUEBA DESC`.

### 9.3 Consultar detalle

```http
GET /valoracion-deportiva/{id}
```

### 9.4 Actualizar

```http
PUT /valoracion-deportiva/{id}
```

No debe permitir modificar `IMC`, `MASA_GRASA_KG`, `MASA_LIBRE_GRASA_KG` ni `AKS` desde payload.

### 9.5 Eliminar

```http
DELETE /valoracion-deportiva/{id}
```

Debe requerir confirmacion en frontend y registrar auditoria.

### 9.6 PDF individual

```http
GET /valoracion-deportiva/{id}/pdf
```

### 9.7 PDF longitudinal

```http
GET /valoracion-deportiva/deportista/{identi}/longitudinal/pdf
```

---

## 10. Validaciones

### 10.1 Reglas generales

| Campo | Regla |
|-------|-------|
| `IDENTI_DEPORTISTA` | Obligatorio. Debe existir en `CDRTablaDeportistas`. |
| `FECHA_PRUEBA` | Obligatoria. No futura. |
| `TALLA_M` | Mayor que 0. Recomendado: 1.00 a 2.50. |
| `PESO_KG` | Mayor que 0. Recomendado: 25 a 250. |
| `PORC_GRASA_CORPORAL` | 0 a 80. |
| `PERIMETRO_ABDOMINAL_CM` | 30 a 200. |
| `FUERZA_PRENSIL_D/I` | 0 a 120. |
| `PESO_MUERTO_KG` | 0 a 400. |
| `CORE_ANTERIOR_SEG` | 0 a 600. |
| `CORE_POSTERIOR_SEG` | 0 a 600. |
| `FC_REPOSO` | 30 a 220. |
| `FC_MAXIMA` | 60 a 240. |
| `FC_REC_15S`, `FC_REC_1M`, `FC_REC_3M` | 30 a 240. |
| `VO2_MAX` | 0 a 100. |
| `FLEXIBILIDAD_PUNTUACION` | Rango configurable segun protocolo. |
| `MOVILIDAD_FMS_PUNTUACION` | 0 a 3 si corresponde a FMS por prueba. |

### 10.2 Valoraciones textuales

Los siguientes campos quedan manuales o por baremos futuros:

- `IMC_VALORACION`
- `PERIMETRO_ABDOMINAL_VALORACION`
- `AKS_VALORACION`
- `GRASA_CORPORAL_VALORACION`
- `FUERZA_PRENSIL_VALORACION`
- `PESO_MUERTO_VALORACION`
- `CORE_ANTERIOR_VALORACION`
- `CORE_POSTERIOR_VALORACION`
- `VO2_MAX_VALORACION`
- `FLEXIBILIDAD_VALORACION`
- `MOVILIDAD_FMS_VALORACION`

No deben automatizarse hasta aprobar baremos oficiales por sexo, edad y protocolo.

---

## 11. Integridad y Transacciones

### 11.1 Integridad referencial

`CDRTablaValoracionDeportiva.IDENTI_DEPORTISTA` referencia a `CDRTablaDeportistas.IDENTI_DEPORTISTA`.

Politica:

```text
ON UPDATE RESTRICT
ON DELETE RESTRICT
```

Esto impide valoraciones huerfanas e impide eliminar deportistas con valoraciones deportivas asociadas.

### 11.2 Integridad de unicidad

Regla:

```text
UNIQUE (IDENTI_DEPORTISTA, FECHA_PRUEBA)
```

Respuesta esperada de API:

```text
409 Conflict
```

cuando se intente crear una segunda valoracion para el mismo deportista y fecha.

### 11.3 Transacciones

Los servicios deben controlar:

```text
db.commit()
db.rollback()
```

Los routers no deben abrir transacciones directamente.

Patron esperado:

```text
router -> schema -> service -> model -> commit/rollback -> audit
```

---

## 12. Interfaz de Usuario

### 12.1 Navegacion

El APK de Valoracion Fisica Deportiva debe tener navegacion propia. Despues del login compartido, el menu principal muestra:

```text
Valoracion Deportiva
Historial Deportivo
Analisis Longitudinal
Deportistas
Deportes
Asignaciones
```

No debe depender de la opcion "Valoracion Corporal" ni de la navegacion principal del APK de somatotipo.

Pantallas compartidas reutilizadas sin duplicar logica:

```text
Login
Deportistas
Deportes
Asignaciones
```

### 12.2 Pantalla principal

Secciones:

1. Busqueda de deportista.
2. Datos generales de la prueba.
3. Antropometria basica.
4. Fuerza.
5. Resistencia.
6. Flexibilidad y movilidad.
7. Observaciones.
8. Resumen calculado.

### 12.3 Indicadores calculados visibles

Mostrar como lectura solamente:

- IMC
- Masa grasa kg
- Masa libre de grasa kg
- AKS

Estos valores no deben tener campos editables.

### 12.4 Historial

Debe permitir:

- Ver pruebas del deportista.
- Comparar fechas.
- Abrir detalle.
- Descargar PDF.
- Eliminar con confirmacion.

### 12.5 Analisis longitudinal

Variables iniciales graficables:

- Peso
- IMC
- Porcentaje de grasa corporal
- Masa grasa
- Masa libre de grasa
- AKS
- Fuerza prensil derecha
- Fuerza prensil izquierda
- Peso muerto
- VO2 max
- Flexibilidad
- Movilidad FMS

---

## 13. Auditoria

Eventos a registrar:

| Accion | Codigo sugerido |
|--------|-----------------|
| Crear valoracion deportiva | `VALORACION_DEPORTIVA_CREATE` |
| Actualizar valoracion deportiva | `VALORACION_DEPORTIVA_UPDATE` |
| Eliminar valoracion deportiva | `VALORACION_DEPORTIVA_DELETE` |
| Descargar PDF individual | `VALORACION_DEPORTIVA_PDF` |
| Descargar PDF longitudinal | `VALORACION_DEPORTIVA_LONGITUDINAL_PDF` |

Recurso:

```text
RESOURCE_TYPE = valoracion_deportiva
RESOURCE_ID = ID_VALORACION_DEPORTIVA
```

---

## 14. Modelo SQLAlchemy

Clase propuesta:

```python
class ValoracionDeportiva(Base):
    __tablename__ = "CDRTablaValoracionDeportiva"

    ID_VALORACION_DEPORTIVA = Column(Integer, primary_key=True, autoincrement=True)
    IDENTI_DEPORTISTA = Column(
        String(20),
        ForeignKey("CDRTablaDeportistas.IDENTI_DEPORTISTA", ondelete="RESTRICT"),
        nullable=False,
    )
    FECHA_PRUEBA = Column(Date, nullable=False)
    LOGIN_USER = Column(String(60))

    # Campos capturados y calculados segun migracion 005.
    deportista = relationship("Deportista")
```

Los campos generados de MySQL deben mapearse como columnas de lectura. La app no debe enviarlos en `INSERT` ni `UPDATE`.

---

## 15. Schemas Pydantic

Schemas sugeridos:

```text
ValoracionDeportivaBase
ValoracionDeportivaCreate
ValoracionDeportivaUpdate
ValoracionDeportivaRead
ValoracionDeportivaListItem
```

Los schemas de entrada no deben incluir:

- `IMC`
- `MASA_GRASA_KG`
- `MASA_LIBRE_GRASA_KG`
- `AKS`
- `CREATED_AT`
- `UPDATED_AT`

Los schemas de salida si deben incluirlos.

---

## 16. Pruebas

### 16.1 Unitarias

- Validacion de rangos.
- Serializacion de schemas.
- Calculo esperado de columnas generadas usando consulta real o fixture SQL.
- Manejo de payload sin campos calculados.

### 16.2 Integracion backend

- Crear valoracion valida.
- Crear valoracion con deportista inexistente debe fallar.
- Crear duplicado por deportista y fecha debe devolver 409.
- Actualizar campos capturados recalcula campos generados.
- Eliminar valoracion existente.
- Eliminar deportista con valoracion deportiva debe devolver 409.

### 16.3 Frontend

- Busqueda de deportista.
- Validacion visual de campos.
- Campos calculados en solo lectura.
- Guardado exitoso.
- Manejo de error por duplicado.
- Historial responsive.

### 16.4 PDF

- PDF individual contiene datos del deportista.
- PDF individual contiene indicadores calculados.
- PDF longitudinal ordena las fechas correctamente.
- PDF no falla con campos opcionales nulos.

### 16.5 Migracion

- La tabla existe.
- La FK existe.
- El indice unico existe.
- El motor es InnoDB.
- Las columnas generadas existen como `STORED`.

---

## 17. Criterios de Aceptacion

| ID | Criterio |
|----|----------|
| AC-001 | Una valoracion deportiva solo puede guardarse para un deportista existente. |
| AC-002 | No se permiten dos valoraciones del mismo deportista en la misma fecha. |
| AC-003 | IMC, masa grasa, masa libre de grasa y AKS se calculan en MySQL. |
| AC-004 | El frontend no permite editar campos calculados. |
| AC-005 | La API no acepta campos calculados en create/update. |
| AC-006 | Toda creacion, actualizacion, eliminacion y PDF queda auditado. |
| AC-007 | El historial lista valoraciones por fecha descendente. |
| AC-008 | El modulo funciona en escritorio y movil sin solapamientos de texto. |
| AC-009 | La eliminacion de deportistas con valoraciones deportivas se bloquea. |
| AC-010 | La suite de pruebas relevante pasa antes de publicar. |
| AC-011 | Se genera un APK independiente de Valoracion Fisica Deportiva. |
| AC-012 | El APK deportivo reutiliza login, deportistas, deportes y asignaciones sin incluir pantallas propias de somatotipo. |

---

## 18. Plan de Implementacion

### Fase 1 - Base de datos

1. Ejecutar migracion `005`.
2. Verificar tabla, FK, unique y columnas calculadas.
3. Actualizar documentacion de integridad referencial.

### Fase 2 - Backend

1. Agregar modelo SQLAlchemy.
2. Agregar schemas Pydantic.
3. Agregar servicio transaccional.
4. Agregar router FastAPI.
5. Registrar router en `src/backend/main.py`.
6. Agregar auditoria.
7. Agregar pruebas backend.

### Fase 3 - Frontend

1. Agregar metodos en `ApiClient`.
2. Crear vista `views/valoracion_deportiva.py`.
3. Parametrizar navegacion y shell por producto/APK.
4. Agregar historial y detalle.
5. Validar responsive.

### Fase 4 - Empaquetado APK independiente

1. Crear punto de entrada del APK deportivo.
2. Configurar nombre visible, icono, rutas y menu del APK deportivo.
3. Reutilizar login, deportistas, deportes y asignaciones.
4. Excluir pantallas propias de somatotipo del menu deportivo.
5. Generar APK de Valoracion Fisica Deportiva y validar instalacion independiente.

### Fase 5 - Reportes y analisis

1. Crear PDF individual.
2. Crear vista longitudinal.
3. Crear PDF longitudinal.
4. Agregar graficos de tendencia.

### Fase 6 - Cierre

1. Ejecutar pruebas.
2. Revisar auditoria.
3. Revisar textos y unidades con equipo de ciencias del deporte.
4. Publicar APK independiente.

---

## 19. Riesgos y Decisiones Pendientes

| Riesgo | Impacto | Mitigacion |
|--------|---------|------------|
| Formula AKS no confirmada por protocolo UTP. | Calculo incorrecto. | Validar formalmente con equipo metodologico. |
| Baremos de valoracion no definidos. | Clasificaciones inconsistentes. | Mantener campos textuales manuales hasta aprobar baremos. |
| VO2 max puede depender de formula especifica del Queen College. | Calculo no reproducible. | Dejar `VO2_MAX` capturado hasta validar formula oficial. |
| Duplicidad entre somatotipo y valoracion deportiva. | Confusion de usuarios. | Separar APKs y explicar diferencias en interfaz. |
| Acoplamiento excesivo con el shell de Somatocarta. | El APK deportivo hereda pantallas no deseadas. | Parametrizar navegacion por producto y probar el menu final del APK. |
| Campos opcionales incompletos. | Reportes con huecos. | PDF y vistas deben tolerar `NULL`. |

---

## 20. Glosario

| Termino | Definicion |
|---------|------------|
| Deportista | Persona registrada en `CDRTablaDeportistas`, incluyendo funcionarios que representan a la UTP. |
| Valoracion deportiva | Bateria fisica aplicada al representante deportivo. |
| IMC | Indice de masa corporal, peso dividido por talla al cuadrado. |
| AKS | Indice de sustancia activa, definido en esta propuesta como masa libre de grasa dividida por talla al cuadrado. |
| FMS | Functional Movement Screen. En esta ficha se usa para movilidad paso de valla. |
| Queen College | Test de banco usado para estimacion de resistencia cardiorrespiratoria. |
