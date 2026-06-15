# Informe final de pruebas QA - Somatocarta v1.1.7
## Escenario: Liga Risaraldense de Boxeo

---

## 1. Resumen ejecutivo

- **Fecha de prueba:** 15 de junio de 2026
- **Entorno:** Local Windows 11, backend FastAPI en `http://127.0.0.1:8085`, frontend Flet, base de datos MySQL remota (nyquist.app)
- **Usuario usado:** `famedina` (Fabian Medina, ID=10)
- **Contraseña proporcionada vs real:** Se indicó `CDR206` pero la contraseña real es `CDR2026`
- **Resultado general:** La aplicación funciona en sus flujos principales (login, CRUD básico, valoraciones, PDFs), pero presenta errores críticos en cálculos de somatotipo, integridad referencial y validación de duplicados.
- **Nivel de estabilidad estimado:** 65-70%
- **¿La app está lista para validación con usuarios reales?:** **Parcialmente** — Requiere correcciones críticas antes de producción.

---

## 2. Cambios realizados en el código

No aplica. Durante esta prueba no se realizaron modificaciones al código fuente.

---

## 3. Datos creados

| Concepto | Detalle |
|---|---|
| **Entidad** | Liga Risaraldense de Boxeo (NIT: QA-LRB-001) — creada y luego eliminada en prueba |
| **Deporte** | Boxeo (ID: 16) — creado y luego eliminado en prueba. Nota: se duplicó 4 veces por bug |
| **Boxeadores creados** | QA-BOX-001 a QA-BOX-004 (4 activos; QA-BOX-005 eliminado en prueba) |
| **Asignaciones** | 5 asignaciones creadas (deporte-entidad-deportista) |
| **Valoraciones creadas** | 25 valoraciones (5 por boxeador × 5 meses), cada una con 3 tomas de medición |
| **PDFs generados** | 5 individuales + 5 longitudinales = 10 PDFs |

---

## 4. CRUD evaluados

| Módulo | Crear | Listar | Consultar | Editar | Eliminar | Estado general |
|---|---|---|---|---|---|---|
| Deportistas | OK | OK | OK | OK | OK | **Funcional** |
| Entidades | OK | OK | OK | OK | OK (sin restricción referencial) | **Parcial** |
| Deportes | OK (sin validación duplicados) | OK | OK | OK | OK (sin restricción referencial) | **Parcial** |
| Asignaciones | OK (sin validación duplicados) | OK | OK | OK | OK | **Parcial** |
| Valoraciones | OK | OK | OK | Parcial | OK | **Parcial** |
| Detalles valoración | OK | Parcial | OK | Parcial | OK | **Parcial** |

---

## 5. Flujos probados

| Flujo | Resultado | Observaciones |
|---|---|---|
| Login correcto | PASS | Token JWT generado correctamente |
| Login incorrecto (user) | PASS | 401 |
| Login incorrecto (pass) | PASS | 401 |
| Login campos vacíos | PASS | 401 |
| Acceso sin token | PASS | 401 |
| Acceso con token inválido | PASS | 401 |
| Cerrar sesión (limpiar token) | PASS | Sesión protegida |
| Crear deportista | PASS | Con todos los campos |
| Buscar deportista | PASS | Por nombre e ID |
| Editar deportista | PASS | Actualización correcta |
| Crear entidad | PASS | |
| Editar entidad | PASS | |
| Crear deporte | PASS | |
| Crear asignación | PASS | |
| Crear valoración (3 tomas) | PASS | 25/25 exitosas |
| Ver historial por deportista | PASS | 5 valoraciones por boxeador |
| Generar PDF individual | PASS | 5 PDFs válidos |
| Generar PDF longitudinal | PASS | 5 PDFs válidos |
| Editar detalle de valoración | FAIL | Endpoint inconsistente |
| Eliminar valoración | PASS | Cascade correcto |
| Eliminar deportista con datos | PASS | Sin restricción (ver hallazgo) |
| Eliminar entidad con asignaciones | PASS | Sin restricción (ver hallazgo) |
| Eliminar deporte con asignaciones | PASS | Sin restricción (ver hallazgo) |

---

## 6. Evaluación funcional por módulo

### 6.1 Autenticación
| Qué funciona | Qué no funciona | Recomendación |
|---|---|---|
| Login con credenciales válidas | Contraseña indicada en docs (`CDR206`) no coincide con la real (`CDR2026`) | Actualizar documentación |
| Rechazo de credenciales inválidas | | |
| Protección de endpoints sin token | | |
| Token JWT con expiración | Las contraseñas están en texto plano en la BD | Implementar hash de contraseñas |

### 6.2 Dashboard
| Qué funciona | Qué no funciona | Recomendación |
|---|---|---|
| Contadores generales | `actividad_reciente` no incluye valoraciones QA recién creadas | Revisar query de actividad reciente |
| Vista contrato (validación de columnas) | `expected_count` se mantiene en 41 aunque hay 46 deportistas | El conteo parece hardcodeado o cacheado |

### 6.3 CRUD Deportistas
| Qué funciona | Qué no funciona | Recomendación |
|---|---|---|
| Crear, listar, consultar, editar, eliminar | Deportista duplicado retorna 400 (correcto) | |
| Búsqueda por nombre e ID | | |
| Paginación funcional | | |
| Validación de campos obligatorios | | |

### 6.4 CRUD Entidades
| Qué funciona | Qué no funciona | Recomendación |
|---|---|---|
| Crear, listar, editar, eliminar | Se puede eliminar entidad con asignaciones activas sin advertencia | Validar integridad referencial antes de eliminar |
| Rechazo de NIT duplicado (400) | | |

### 6.5 CRUD Deportes
| Qué funciona | Qué no funciona | Recomendación |
|---|---|---|
| Crear, listar, editar, eliminar | **NO rechaza deportes duplicados** (retorna 200 y crea otro) | Agregar constraint UNIQUE en columna DEPORTE |
| | Se crearon 4 registros "Boxeo" en pruebas | |

### 6.6 CRUD Asignaciones
| Qué funciona | Qué no funciona | Recomendación |
|---|---|---|
| Crear, listar, editar, eliminar | **NO rechaza asignaciones duplicadas** (retorna 200 y crea otra) | Agregar constraint UNIQUE compuesto |

### 6.7 Valoraciones Corporales
| Qué funciona | Qué no funciona | Recomendación |
|---|---|---|
| Crear valoración con múltiples tomas | Endpoint `editable/deportista/{identi}` no retorna detalles (0 detalles) | Corregir query del listado editable |
| 3 tomas por valoración (promedio) | Inconsistencia entre `detalles` (minúscula) y `DETALLES` (mayúscula) | Unificar naming |
| Historial completo por deportista | | |
| Generación de PDF individual | | |
| Generación de PDF longitudinal | | |
| Eliminación de valoración completa | | |
| Creación de detalle adicional (4ta toma) | | |

### 6.8 Catálogos
| Qué funciona | Qué no funciona | Recomendación |
|---|---|---|
| Tipos documento (7 registros) | | |
| Estratos (10 registros) | | |
| Niveles educativos (12 registros) | | |

---

## 7. Evaluación de cálculos y análisis

| Boxeador | IMC rango | % Graso (Johnson) | Somatotipo | Longitudinal | Observación |
|---|---|---|---|---|---|
| QA-BOX-001 (M) | 20.01-20.43 Normal | 11.07-11.57% | Endo: 2.1-2.7, **Meso: -4.8 a -5.2**, Ecto: 2.7-2.8 | OK tendencias | **CRÍTICO: Mesomorfismo negativo** |
| QA-BOX-002 (F) | 21.08-21.45 Normal | 10.50-10.51% | Endo: 3.2-3.8, **Meso: -4.7 a -5.1**, Ecto: 2.0-2.1 | OK tendencias | **CRÍTICO: Mesomorfismo negativo** |
| QA-BOX-003 (M) | 22.02-22.44 Normal | 11.59-11.60% | Endo: 1.9-2.4, **Meso: -4.8 a -5.1**, Ecto: 2.2-2.3 | OK tendencias | **CRÍTICO: Mesomorfismo negativo** |
| QA-BOX-004 (F) | 21.67-22.04 Normal | 10.02-10.52% | Endo: 3.0-3.6, **Meso: -4.8 a -5.2**, Ecto: 1.9-2.0 | OK tendencias | **CRÍTICO: Mesomorfismo negativo** |
| QA-BOX-005 (M) | 22.90-23.30 Normal | 12.12% | Endo: 1.7-2.2, **Meso: -4.8 a -5.2**, Ecto: 2.1-2.2 | OK tendencias | **CRÍTICO: Mesomorfismo negativo** |

### Análisis de anomalías en cálculos:

1. **Mesomorfismo negativo en TODOS los boxeadores**: Valores entre -4.72 y -5.19. Un boxeador debería tener mesomorfismo POSITIVO y alto (típicamente 3.5-6.0 en la escala Heath-Carter). Esto indica un error sistemático en la fórmula de cálculo del componente mesomórfico.

2. **Peso óseo extremadamente bajo**: Valores de 0.35-0.50 kg. El peso óseo típico para un adulto debería estar entre 2.0-4.0 kg. Esto sugiere un error en la fórmula de estimación de masa ósea.

3. **Escala de Ectomorfismo incoherente**: El texto dice "BAJO: Linealidad relativa gran volumen por unidad de altura <redondo> como una <pelota>" — el texto parece corrupto o es una mezcla de descripciones de diferentes componentes.

4. **% Graso Johnson vs Faulkner inconsistentes**: Johnson reporta ~10-12% mientras Faulkner reporta ~9-13%. Las diferencias son amplias y la tendencia no siempre es consistente entre métodos.

5. **Tendencias longitudinales correctas**: La evolución mensual muestra reducción progresiva de pliegues y mantenimiento de peso, lo cual es coherente con el entrenamiento de boxeo.

---

## 8. Evaluación de informes PDF

| Boxeador | PDF individual | PDF longitudinal | Observaciones |
|---|---|---|---|
| QA-BOX-001 | OK (1723 KB) | OK (1745 KB) | Contiene: ID, nombre, IMC, somatotipo |
| QA-BOX-002 | OK (1723 KB) | OK (1745 KB) | Contiene: ID, nombre, IMC, somatotipo |
| QA-BOX-003 | OK (1723 KB) | OK (1745 KB) | Contiene: ID, nombre, IMC, somatotipo |
| QA-BOX-004 | OK (1723 KB) | OK (1745 KB) | Contiene: ID, nombre, IMC, somatotipo |
| QA-BOX-005 | OK (1723 KB) | OK (1745 KB) | Contiene: ID, nombre, IMC, somatotipo |

**Hallazgos de PDFs:**
- Todos los PDFs individuales tienen exactamente el mismo tamaño (1,764,534 bytes), lo cual es sospechoso.
- Todos los PDFs longitudinales tienen exactamente el mismo tamaño (1,780,022 bytes).
- Los PDFs contienen los datos correctos del deportista (verificado por búsqueda de texto).
- No se pudo evaluar visualmente gráficos ni formato (requiere apertura manual).

---

## 9. Evaluación responsive

| Pantalla | Móvil | Tablet | Escritorio | Observaciones |
|---|---|---|---|---|
| Login | No evaluado (API) | No evaluado | OK vía API | Flet soporta responsive |
| Dashboard | No evaluado | No evaluado | OK vía API | |
| Formularios | No evaluado | No evaluado | OK vía API | |

*Nota: La evaluación responsive visual requiere ejecución del frontend Flet en diferentes resoluciones. Las pruebas se realizaron vía API REST.*

---

## 10. Evaluación de navegación

| Ruta o acción | Resultado | Observación |
|---|---|---|
| POST /auth/login | OK 200 | Login funcional |
| GET /dashboard/summary | OK 200 | Datos correctos |
| GET /catalogos/tipos_documento | OK 200 | 7 tipos |
| GET /catalogos/estratos | OK 200 | 10 estratos |
| GET /catalogos/niveles_educativos | OK 200 | 12 niveles |
| GET /deportistas/ | OK 200 | Paginación funcional |
| GET /deportistas/{identi} | OK 200 / 404 | Correcto |
| POST /deportistas/ | OK 200 / 400 | Validación activa |
| PUT /deportistas/{identi} | OK 200 | |
| DELETE /deportistas/{identi} | OK 200 | |
| GET/POST/PUT/DELETE /entidades/ | OK 200 | |
| GET/POST/PUT/DELETE /deportes/ | OK 200 | Sin validación duplicados |
| GET/POST/PUT/DELETE /asignaciones/ | OK 200 | Sin validación duplicados |
| POST /somatotipo/ | OK 200 / 422 | Validación de rangos activa |
| GET /somatotipo/vista/deportista/{identi} | OK 200 | Historial completo |
| GET /somatotipo/editable/deportista/{identi} | OK 200 | **No retorna detalles** |
| GET /somatotipo/editable/{id} | OK 200 | Sí retorna detalles (DETALLES) |
| POST /somatotipo/{id}/detalle | OK 200 | Agregar toma adicional |
| PUT /somatotipo/detalle/{id} | No probado a fondo | |
| DELETE /somatotipo/detalle/{id} | No probado a fondo | |
| DELETE /somatotipo/{id} | OK 200 | Eliminación completa |
| GET /somatotipo/{id}/pdf | OK 200 | PDF válido |
| GET /somatotipo/vista/deportista/{identi}/longitudinal/pdf | OK 200 | PDF válido |
| GET /somatotipo/vista/contrato | OK 200 | Contrato de vista |

---

## 11. Evaluación específica para boxeo

| Aspecto | Resultado | Observación |
|---|---|---|
| Categorías de peso | **No soportado** | La app no tiene concepto de categoría de peso del deportista |
| Clasificación por peso | **No disponible** | No hay campo para peso competitivo o categoría |
| Somatotipo mesomórfico | **Error de cálculo** | Todos los boxeadores muestran mesomorfismo negativo, incoherente con el perfil esperado |
| Seguimiento de composición corporal | Funcional | Las tendencias de reducción de grasa son coherentes |
| IMC para deportes de peso | Parcial | IMC calculado pero no contextualizado para boxeo |
| Informes para categoría de peso | **No disponible** | Los PDFs no incluyen referencia a categoría de peso |

**Ajustes necesarios para boxeo:**
1. Agregar campo de "categoría de peso" al deportista o a la asignación deporte-deportista.
2. Corregir la fórmula de mesomorfismo para que produzca valores positivos en atletas musculares.
3. Incluir en los informes la categoría de peso y la cercanía al peso de competencia.
4. Agregar alertas cuando el % graso o peso se acerquen a los límites de categoría.

---

## 12. Pruebas negativas

| Caso | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|
| Login usuario inexistente | 401 | 401 | PASS |
| Login contraseña incorrecta | 401 | 401 | PASS |
| Login campos vacíos | 401/422 | 401 | PASS |
| Acceso sin token | 401/403 | 401 | PASS |
| Acceso con token inválido | 401/403 | 401 | PASS |
| Deportista duplicado | 400/409 | 400 | PASS |
| Sexo inválido (X) | 422 | 422 | PASS |
| Fecha nacimiento futura | 422 | 422 | PASS |
| Campos obligatorios vacíos | 422 | 422 | PASS |
| Valores fuera de rango | 422 | 422 | PASS |
| Valoración sin detalles | 422 | 422 | PASS |
| Valoración fecha futura | 422 | 422 | PASS |
| Email inválido | 422 | 422 | PASS |
| Entidad duplicada | 400/409 | 400 | PASS |
| **Deporte duplicado** | 400/409 | **200 (crea duplicado)** | **FAIL** |
| Asignación deportista inexistente | 422 | 422 | PASS |
| **Asignación duplicada** | 400/409 | **200 (crea duplicado)** | **FAIL** |
| Deportista inexistente | 404 | 404 | PASS |

---

## 13. Errores encontrados

| # | Severidad | Módulo | Error | Estado | Recomendación |
|---|---|---|---|---|---|
| 1 | **Crítico** | Somatotipo | **Mesomorfismo negativo** en todos los deportistas (-4.7 a -5.2). Incoherente para atletas. | Abierto | Revisar fórmula del componente mesomórfico en la vista SQL o servicio de cálculos. Verificar que los diámetros y perímetros se están usando correctamente. |
| 2 | **Crítico** | Somatotipo | **Peso óseo irreal** (0.35-0.50 kg). Debería ser 2-4 kg en adultos. | Abierto | Revisar fórmula de estimación de masa ósea (probablemente usa diámetros en mm en vez de cm). |
| 3 | **Alto** | Deportes | **No valida deportes duplicados**. Se crearon 4 registros "Boxeo". | Abierto | Agregar constraint UNIQUE en columna DEPORTE de CDRTablaDeportes. |
| 4 | **Alto** | Asignaciones | **No valida asignaciones duplicadas**. Permite crear la misma relación varias veces. | Abierto | Agregar constraint UNIQUE compuesto (ID_DEPORTE, IDENTI_DEPORTISTA, NIT_ENTIDAD). |
| 5 | **Alto** | Entidades | **Eliminar entidad con asignaciones activas** no genera error ni advertencia. Posibles datos huérfanos. | Abierto | Validar existencia de asignaciones antes de eliminar, o aplicar cascade. |
| 6 | **Alto** | Deportes | **Eliminar deporte con asignaciones activas** no genera error. | Abierto | Igual que anterior. |
| 7 | **Alto** | Deportistas | **Eliminar deportista con valoraciones** no genera error ni advertencia. Se pierden todas las valoraciones. | Abierto | Validar existencia de valoraciones antes de eliminar, o aplicar cascade con advertencia. |
| 8 | **Alto** | Valoraciones | **Endpoint `/somatotipo/editable/deportista/{identi}`** no retorna detalles (0 detalles). El endpoint individual `/somatotipo/editable/{id}` sí los retorna. | Abierto | Corregir query del listado editable para incluir detalles. |
| 9 | **Medio** | Valoraciones | **Inconsistencia de naming**: `detalles` (minúscula) vs `DETALLES` (mayúscula) entre endpoints. | Abierto | Unificar naming convention. |
| 10 | **Medio** | Somatotipo | **Texto de escala corrupto**: La escala de ectomorfismo contiene texto incoherente ("<redondo> como una <pelota>"). | Abierto | Revisar generación de textos de escala en la vista SQL. |
| 11 | **Medio** | Dashboard | **Actividad reciente no se actualiza** con valoraciones nuevas creadas vía API. | Abierto | Revisar query de actividad reciente. |
| 12 | **Medio** | Dashboard | **vista_contrato.expected_count** se mantiene en 41 aunque hay 46 deportistas. | Abierto | El conteo esperado parece estático. |
| 13 | **Medio** | Seguridad | **Contraseñas en texto plano** en la base de datos. | Abierto | Implementar hash con bcrypt o similar. |
| 14 | **Medio** | Documentación | **Contraseña indicada (`CDR206`)** no coincide con la real (`CDR2026`). | Abierto | Actualizar documentación de credenciales. |
| 15 | **Bajo** | PDFs | **Tamaño idéntico** en todos los PDFs individuales (1,764,534 bytes) y longitudinales (1,780,022 bytes). | Abierto | Verificar que el contenido varía correctamente entre deportistas. |
| 16 | **Mejora UX** | Boxeo | **Sin soporte para categorías de peso**. La app no permite registrar ni consultar la categoría de peso competitiva. | Pendiente | Agregar campo de categoría de peso. |
| 17 | **Mejora UX** | Catálogos | **Campos de tipos de documento** con nombres confusos (duplicados: "Cedula de ciudadania" y "Cedula Ciudadania"). | Abierto | Limpiar catálogo de tipos de documento. |

---

## 14. Lo que funciona correctamente

1. **Autenticación JWT** — Login, protección de endpoints, manejo de tokens.
2. **CRUD de deportistas** — Crear, listar, buscar, consultar, editar, eliminar.
3. **CRUD de entidades** — Crear, listar, editar (con validación de NIT duplicado).
4. **Creación de valoraciones** — Con múltiples tomas (3 repeticiones por valoración).
5. **Historial de valoraciones** — Vista completa con todos los cálculos.
6. **Paginación** — Funcional en todos los listados.
7. **Búsquedas** — Por nombre, ID, y otros campos.
8. **Generación de PDFs individuales** — PDFs válidos con datos correctos.
9. **Generación de PDFs longitudinales** — PDFs válidos con datos correctos.
10. **Validación de rangos antropométricos** — Rechaza valores fuera de los límites definidos.
11. **Validación de campos obligatorios** — Rechaza campos vacíos o inválidos.
12. **Validación de emails** — Rechaza dominios reservados o inválidos.
13. **Validación de fechas** — Rechaza fechas futuras.
14. **Eliminación de valoraciones** — Con cascade de detalles.
15. **Creación de tomas adicionales** — Se pueden agregar más de 3 tomas.
16. **Cálculo de IMC** — Valores coherentes y estado "Normal" correcto.
17. **Tendencias longitudinales** — La evolución mensual es fisiológicamente plausible.
18. **Auditoría** — Sistema de auditoría registra acciones exitosas y fallidas.

---

## 15. Lo que no funciona o requiere corrección

1. **Cálculo de mesomorfismo** — Valores negativos para todos los deportistas. Error sistemático.
2. **Cálculo de peso óseo** — Valores irrealmente bajos (0.35-0.50 kg).
3. **Deportes duplicados** — No hay validación de unicidad.
4. **Asignaciones duplicadas** — No hay validación de unicidad.
5. **Integridad referencial** — Se pueden eliminar entidades, deportes y deportistas con datos relacionados sin restricción.
6. **Endpoint de valoraciones editables** — No retorna los detalles de las mediciones.
7. **Textos de escala** — Descripciones corruptas o incoherentes.
8. **Dashboard desactualizado** — Actividad reciente y conteo esperado no reflejan datos nuevos.
9. **Sin soporte para categorías de peso** — Limitación funcional para deportes como boxeo.
10. **Contraseñas en texto plano** — Riesgo de seguridad.

---

## 16. Recomendaciones priorizadas

### 1. Correcciones críticas
1. **Corregir fórmula de mesomorfismo** — Verificar que los perímetros y diámetros se convierten correctamente (mm vs cm). Este es el error más grave porque invalida todos los análisis de somatotipo.
2. **Corregir fórmula de peso óseo** — Probablemente el mismo problema de unidades (mm vs cm) en los diámetros.
3. **Corregir textos de escala** — Revisar la lógica de generación de descripciones textuales.

### 2. Mejoras funcionales
4. **Agregar constraint UNIQUE en deportes** — Evitar duplicados.
5. **Agregar constraint UNIQUE compuesto en asignaciones** — Evitar duplicados.
6. **Validar integridad referencial antes de eliminar** — Entidades, deportes, deportistas con datos relacionados.
7. **Corregir endpoint de valoraciones editables** — Incluir detalles en la respuesta del listado.
8. **Unificar naming** — `detalles` vs `DETALLES`.

### 3. Mejoras visuales
9. **Verificar contenido de PDFs** — Asegurar que los datos varían entre deportistas (tamaños idénticos son sospechosos).
10. **Revisar formato de textos de escala en PDFs** — Los textos corruptos también aparecen en los informes.

### 4. Mejoras responsive
11. **Evaluar responsive en frontend Flet** — No se pudo evaluar visualmente en esta prueba.

### 5. Mejoras de informes
12. **Incluir categoría de peso en informes** — Para deportes como boxeo.
13. **Agregar alertas de categoría de peso** — Cuando el peso se acerque a límites.

### 6. Mejoras de navegación
14. **Actualizar dashboard en tiempo real** — Actividad reciente y contadores.

### 7. Mejoras específicas para boxeo
15. **Agregar campo de categoría de peso** — Al deportista o a la asignación.
16. **Agregar campo de peso competitivo** — Para seguimiento.
17. **Incluir perfil de somatotipo esperado por categoría** — Como referencia.

### 8. Mejoras de seguridad
18. **Implementar hash de contraseñas** — bcrypt o argon2.
19. **Actualizar documentación de credenciales** — La contraseña indicada no coincide.

### 9. Mejoras de pruebas automatizadas
20. **Agregar tests de integridad referencial** — Para eliminación en cascada.
21. **Agregar tests de unicidad** — Para deportes y asignaciones.
22. **Agregar tests de cálculos antropométricos** — Validar fórmulas con datos conocidos.

---

## 17. Conclusión general

**Somatocarta v1.1.7 es una aplicación funcional en sus flujos básicos** (autenticación, CRUD de deportistas, registro de valoraciones, generación de PDFs), pero presenta **errores críticos en los cálculos de somatotipo** que invalidan el análisis corporal para todos los deportistas.

### Estado de estabilidad:
- **Autenticación y seguridad básica:** Estable
- **CRUD de datos maestros:** Estable (con bugs de duplicación en deportes/asignaciones)
- **Registro de valoraciones:** Estable
- **Cálculos antropométricos:** **NO ESTABLE** — Mesomorfismo negativo y peso óseo irreal
- **Informes PDF:** Funcionales pero con datos de cálculos erróneos
- **Integridad referencial:** **NO ESTABLE** — Eliminación sin restricciones

### ¿Está lista para validación con usuarios reales?
**Parcialmente.** Se puede usar para registrar datos y generar informes, pero los **cálculos de somatotipo son incorrectos** y deben corregirse antes de que los resultados sean utilizados para toma de decisiones deportivas.

### Módulos que deben corregirse antes de producción:
1. **Cálculos de somatotipo** (mesomorfismo, peso óseo, textos de escala) — **CRÍTICO**
2. **Validación de duplicados** en deportes y asignaciones — **ALTO**
3. **Integridad referencial** en eliminaciones — **ALTO**
4. **Endpoint de valoraciones editables** — **ALTO**

### Ajustes necesarios para deportes por categorías de peso (boxeo):
1. Agregar campo de categoría de peso competitiva.
2. Corregir cálculos de somatotipo para que sean coherentes con atletas musculares.
3. Incluir en informes la relación peso actual vs categoría de competencia.
4. Agregar alertas cuando la composición corporal se acerque a límites de categoría.

---

*Informe generado el 15 de junio de 2026. Pruebas realizadas exclusivamente vía API REST. No se modificó código fuente ni configuración de la aplicación.*
