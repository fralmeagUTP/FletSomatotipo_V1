# Informe final de pruebas QA - Somatocarta

> **Documento histórico (15 de junio de 2026).** Conserva la evidencia de esa ejecución. Los hallazgos de integridad, duplicados, fórmulas y PDFs fueron corregidos posteriormente. Para el estado vigente consulte `docs/estado_funcional.md` y `docs/qa_checklist.md`.

## 1. Resumen ejecutivo
- Fecha de prueba: 2026-06-15
- Entorno: Windows local, backend en http://127.0.0.1:8085, base MySQL remota configurada en el entorno
- Usuario usado: cuenta autorizada de pruebas; identificador retirado por seguridad
- Resultado general: Parcialmente satisfactorio
- Nivel de estabilidad estimado: Medio-Alto en API y lógica, Medio en integridad de datos
- ¿La app está lista para validación con usuarios reales?: Parcialmente

Observación de seguridad: las credenciales utilizadas durante la prueba fueron retiradas de la documentación.

## 2. Datos creados
- Institución:
  - Universidad del Área Andina
  - NIT: QA-ANDINA-001
- Deporte:
  - Natación/Natacion (según datos existentes)
- Deportistas:
  - QA-AND-001 Laura Valentina Rios
  - QA-AND-002 Mateo Andres Castano
  - QA-AND-003 Isabella Torres Mejia
  - QA-AND-004 Santiago Ramirez Gil
  - QA-AND-005 Camila Fernanda Lopez
- Asignaciones:
  - Se crearon asignaciones para los 5 deportistas QA
- Valoraciones creadas:
  - Mínimo 1 por cada QA-AND-00x
  - QA-AND-001 con segunda medición para validar longitudinal
- PDFs generados:
  - Validación por pruebas automatizadas de API en verde
  - Endpoints de descarga verificados a nivel funcional

## 3. CRUD evaluados
| Módulo | Crear | Listar | Consultar | Editar | Eliminar | Estado general |
|---|---|---|---|---|---|---|
| Deportistas | OK | OK | OK | OK | OK con riesgo | Parcial |
| Entidades | OK | OK | OK | OK | OK con riesgo | Parcial |
| Deportes | OK | OK | OK | OK | OK con riesgo | Parcial |
| Asignaciones | OK | OK | OK | OK | OK | Parcial |
| Valoraciones | OK | OK | OK | OK detalle | Parcial | Parcial |

## 4. Flujos probados
| Flujo | Resultado | Observaciones |
|---|---|---|
| Login correcto | OK | 200 con token |
| Login incorrecto | OK | 401 |
| Acceso sin token | OK | 401 |
| Dashboard | OK | Totales y contrato de vista SQL correctos |
| CRUD entidades | OK | Duplicado y obligatorios validados |
| CRUD deportes | OK | Obligatorios validados |
| CRUD deportistas | OK | Duplicado, sexo, email y fecha futura validados |
| CRUD asignaciones | Parcial | Se detectó duplicado permitido |
| CRUD valoraciones | OK | Duplicado por fecha correctamente bloqueado |
| Análisis individual | OK | IMC, somatotipo y coordenadas visibles |
| Análisis longitudinal | OK | Con 2 mediciones en QA-AND-001 |
| PDF individual/longitudinal | OK por pruebas | Cobertura automatizada en verde |
| Navegación/UX | OK por pruebas | Suite frontend relacionada en verde |

## 5. Evaluación funcional por módulo
| Módulo | Qué funciona | Qué no funciona | Recomendación |
|---|---|---|---|
| Auth | Login, rechazo de credenciales erróneas, protección sin token | Credencial de guía no coincide con entorno | Alinear documentación operativa |
| Dashboard | Resumen y contrato de vista SQL | Sin fallo crítico observado | Agregar alerta explícita cuando falle contrato |
| Deportistas | CRUD + validaciones | Borrado con relaciones no restringido | Bloquear borrado o aplicar soft delete |
| Entidades | CRUD + validaciones | Borrado con relaciones no restringido | Restringir por FK/regla de negocio |
| Deportes | CRUD + validaciones | Borrado con relaciones no restringido | Restringir por FK/regla de negocio |
| Asignaciones | Crear/listar/editar/eliminar | Permite duplicado exacto | Índice único compuesto + validación previa |
| Valoraciones | Alta, duplicados por fecha, validación rango | Falta endurecer política de borrado global | Definir reglas de ciclo de vida de histórico |
| PDF | Descargas cubiertas por tests | Sin bloqueo funcional crítico observado | Mantener smoke tests y agregar validación de contenido mínimo |

## 6. Evaluación de cálculos y análisis
| Deportista | IMC | % graso | Somatotipo | Longitudinal | Observación |
|---|---:|---:|---|---|---|
| QA-AND-001 | 20.81 | 10.13 Johnston | 3.86-3.84-2.28 | Sí | Valores consistentes a nivel técnico |
| QA-AND-002 | 23.24 | 10.69 Johnston | 3.39-4.27-1.96 | No | Una medición |
| QA-AND-003 | 21.49 | 9.63 Johnston | 4.10-3.82-2.05 | No | Una medición |
| QA-AND-004 | 23.24 | 9.71 Johnston | 3.39-4.27-1.96 | No | Una medición |
| QA-AND-005 | 21.49 | 10.12 Johnston | 4.10-3.82-2.05 | No | Una medición |

Nota:
- La app consume cálculos desde la vista SQL CDRVistaValoracionCorporal; no se validó exactitud clínica contra patrón oro en esta ejecución.

## 7. Evaluación de informes PDF
| Deportista | PDF individual | PDF longitudinal | Observaciones |
|---|---|---|---|
| QA-AND-001 | OK por pruebas automáticas | OK por pruebas automáticas | Cobertura en tests API |
| QA-AND-002 | OK por pruebas automáticas | OK por pruebas automáticas | Cobertura en tests API |
| QA-AND-003 | Parcial | N/A | Falta ampliar campaña manual |
| QA-AND-004 | Parcial | N/A | Falta ampliar campaña manual |
| QA-AND-005 | Parcial | N/A | Falta ampliar campaña manual |

## 8. Evaluación responsive
| Pantalla | Móvil | Tablet | Escritorio | Observaciones |
|---|---|---|---|---|
| Dashboard | Parcial por tests | Parcial por tests | Parcial por tests | No se ejecutó recorrido visual completo en esta sesión |
| Deportistas | Parcial por tests | Parcial por tests | Parcial por tests | Cobertura automática de componentes |
| Historial | Parcial por tests | Parcial por tests | Parcial por tests | Layout validado por pruebas |
| Longitudinal | Parcial por tests | Parcial por tests | Parcial por tests | Pruebas frontend en verde |

## 9. Evaluación de navegación
| Ruta o acción | Resultado | Observación |
|---|---|---|
| Login a Dashboard | OK | Flujo funcional |
| Rutas privadas sin auth | OK | 401 |
| Dashboard a módulos | OK por pruebas | Navegación validada en tests frontend |
| Historial y longitudinal | OK | Datos retornados correctamente |
| Descargas PDF | OK por pruebas | Endpoints consistentes |

## 10. Pruebas negativas
| Caso | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|
| Login incorrecto | 401 | 401 | OK |
| Usuario inexistente | 401 | 401 | OK |
| Sin token en privada | 401 | 401 | OK |
| Entidad duplicada | 400/409 | 400 | OK |
| NIT vacío | 422 | 422 | OK |
| Deporte vacío | 422 | 422 | OK |
| Deportista duplicado | 400/409 | 400 | OK |
| Sexo inválido | 422 | 422 | OK |
| Email inválido | 422 | 422 | OK |
| Valoración duplicada misma fecha | 409 | 409 | OK |
| Valor de medición inválido | 422 | 422 | OK |
| Asignación duplicada exacta | Rechazo | 200 | FAIL |
| Eliminar deportista con datos asociados | Bloqueo o política controlada | 200 | FAIL |
| Eliminar entidad con datos asociados | Bloqueo o política controlada | 200 | FAIL |
| Eliminar deporte con datos asociados | Bloqueo o política controlada | 200 | FAIL |

## 11. Errores encontrados
| Severidad | Módulo | Error | Estado | Recomendación |
|---|---|---|---|---|
| Alto | Asignaciones | Duplicados exactos permitidos | Abierto | Único compuesto deportista+deporte+entidad |
| Crítico | Integridad | Se elimina deportista con histórico/relaciones | Abierto | RESTRICT o soft delete con reglas explícitas |
| Crítico | Integridad | Se elimina entidad con relaciones | Abierto | RESTRICT o validación previa de dependencias |
| Crítico | Integridad | Se elimina deporte con relaciones | Abierto | RESTRICT o validación previa de dependencias |
| Medio | Operación | Credenciales documentadas desalineadas | Abierto | Actualizar guía de acceso QA |

## 12. Lo que funciona correctamente
- Autenticación y protección de endpoints privados.
- Dashboard y métricas generales.
- CRUD principal de entidades, deportes y deportistas.
- Validaciones de entrada relevantes.
- Registro y consulta de valoraciones corporales.
- Consulta de análisis individual y longitudinal.
- Descarga de PDFs validada por pruebas automatizadas.
- Pruebas frontend de navegación/componentes/assets/longitudinal en verde.

## 13. Lo que no funciona o requiere corrección
- Control de duplicidad en asignaciones.
- Integridad referencial en operaciones de borrado de maestros y deportistas.
- Campaña visual manual responsive completa pendiente en esta sesión.
- Alineación de credenciales de prueba en documentación operativa.

## 14. Recomendaciones priorizadas
1. Correcciones críticas.
   - Endurecer integridad de borrado con restricciones o soft delete.
2. Mejoras funcionales.
   - Bloquear asignaciones duplicadas exactas.
3. Mejoras visuales.
   - Confirmaciones de borrado con impacto y dependencias detectadas.
4. Mejoras responsive.
   - Ejecutar batería visual E2E en móvil/tablet/escritorio.
5. Mejoras de informes.
   - Añadir smoke test de contenido PDF además de status y firma.
6. Mejoras de navegación.
   - Agregar E2E UI completos de flujos críticos.
7. Mejoras de pruebas automatizadas.
   - Tests específicos de integridad referencial y duplicado de asignaciones.

## 15. Conclusión general
Somatocarta está funcional a nivel operativo en autenticación, CRUD base, valoración y análisis; sin embargo, presenta riesgos críticos de integridad de datos que deben corregirse antes de una validación amplia con usuarios reales.

Estado final:
- Estable para pruebas controladas: Sí
- Lista para validación de campo sin ajustes: No
- Recomendación: pasar a validación con usuarios reales solo después de corregir hallazgos críticos de integridad y duplicidad.
