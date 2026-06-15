# Informe de redundancias documentales — Somatocarta

**Fecha:** 15 de junio de 2026
**Archivos analizados:** 22 documentos en `docs/`

---

## 1. Inventario completo de `docs/`

| # | Archivo | Tamaño | Categoría |
|---|---------|--------|-----------|
| 1 | `especificacion_sdd_somatocarta.md` | 24.7 KB | Especificación SDD original |
| 2 | `somatocarta_spec.md` | 30.8 KB | Spec Kit (nueva especificación) |
| 3 | `architecture.md` | 9.1 KB | Arquitectura técnica (nueva) |
| 4 | `arquitectura.md` | 3.7 KB | Arquitectura técnica (vieja) |
| 5 | `modules.md` | 15.9 KB | Módulos funcionales |
| 6 | `formulas_somatotipo.md` | 3.2 KB | Fórmulas y cálculos |
| 7 | `user_guide.md` | 8.4 KB | Guía de usuario |
| 8 | `EJECUTAR_POWERSHELL.txt` | ~3 KB | Guía de ejecución |
| 9 | `comandos.txt` | ~1.5 KB | Referencia rápida de comandos |
| 10 | `testing_plan.md` | 9.2 KB | Plan de pruebas |
| 11 | `qa_checklist.md` | 7.7 KB | Checklist de evaluación QA |
| 12 | `informe_qa_boxeo.md` | ~16 KB | Informe QA escenario boxeo |
| 13 | `informe_qa_somatocarta.md` | ~7 KB | Informe QA escenario natación |
| 14 | `documentation_inventory.md` | 7.2 KB | Inventario documental |
| 15 | `deprecated_docs_report.md` | 3.1 KB | Reporte de obsoletos |
| 16 | `changelog_documentation.md` | 2.1 KB | Changelog documental |
| 17 | `informe_final_documentacion.md` | 10.7 KB | Informe final de actualización |
| 18 | `informe_final_sdd.md` | ~3.5 KB | Informe final SDD alternativo |
| 19 | `publicacion.md` | 2.8 KB | Checklist de publicación |
| 20 | `uploads.md` | 1.4 KB | Política de uploads |
| 21 | `AUDITORIA_SISTEMA.md` | ~16 KB | Plan de auditoría + código |
| 22 | `GUIA_GITHUB.md` | ~1 KB | Guía genérica de GitHub |

---

## 2. Redundancias detectadas

### 2.1. CRÍTICA: Dos especificaciones SDD superpuestas

| Documento | Contenido |
|-----------|-----------|
| `especificacion_sdd_somatocarta.md` | SDD original (881 líneas). Cubre arquitectura, componentes, modelo de datos, contratos API, flujos, diseño, validaciones, seguridad, pruebas, backlog. |
| `somatocarta_spec.md` | Spec Kit nuevo (737 líneas). Cubre overview, problem statement, goals, non-goals, personas, user stories, FR, NFR, domain model, data requirements, business rules, UX, reporting, testing, acceptance criteria, open questions, future work. |

**Problema:** Ambos documentos describen el mismo sistema con enfoques ligeramente diferentes. Hay ~60% de contenido superpuesto (arquitectura, APIs, modelos, validaciones, pruebas). Un desarrollador no sabrá cuál consultar.

**Recomendación:** **Fusionar en un solo documento.** Usar `somatocarta_spec.md` como base (estructura Spec Kit más completa) e incorporar las secciones únicas de `especificacion_sdd_somatocarta.md`:
- Sección 5.2 (Vistas frontend detalladas)
- Sección 7 (Contratos API con payloads JSON)
- Sección 8 (Flujos paso a paso)
- Sección 9 (Diseño de interfaz con orden de información)
- Sección 13 (Evaluación arquitectónica con fortalezas/debilidades)
- Sección 14 (Decisiones de diseño vigentes)

**Acción:** Fusionar → `docs/specs/somatocarta_spec.md` (documento único de especificación).

---

### 2.2. ALTA: Dos documentos de arquitectura

| Documento | Contenido |
|-----------|-----------|
| `architecture.md` | Arquitectura nueva (actualizada), incluye los 7 routers, 6 servicios, auditoría, endpoints completos, generación PDF. |
| `arquitectura.md` | Arquitectura vieja con nota de redirección a `architecture.md`. |

**Problema:** `arquitectura.md` ya tiene una nota de redirección pero sigue ocupando espacio. Si se mantiene, genera confusión sobre cuál es la fuente de verdad.

**Recomendación:** **Eliminar `arquitectura.md`.** Todo su contenido válido ya está en `architecture.md`.

---

### 2.3. ALTA: Dos informes finales de la misma sesión

| Documento | Contenido |
|-----------|-----------|
| `informe_final_documentacion.md` | Informe final completo (10.7 KB) con 11 secciones. |
| `informe_final_sdd.md` | Informe final alternativo (~3.5 KB) con 11 secciones similares. |

**Problema:** Ambos documentos resumen la misma sesión de trabajo. Tienen secciones casi idénticas (resumen, inventario, documentos creados, recomendaciones, confirmación de restricciones).

**Recomendación:** **Eliminar `informe_final_sdd.md`.** `informe_final_documentacion.md` es más completo y detallado.

---

### 2.4. MEDIA: Guía de ejecución + referencia de comandos

| Documento | Contenido |
|-----------|-----------|
| `EJECUTAR_POWERSHELL.txt` | Instrucciones completas de ejecución (81 líneas): backend, frontend, configuración, verificación, pruebas, APK. |
| `comandos.txt` | Lista rápida de comandos (38 líneas): los mismos comandos pero sin explicación. |

**Problema:** `comandos.txt` es un subconjunto de `EJECUTAR_POWERSHELL.txt`. Ambos están en formato `.txt` con formato informal. Además, ambos están desactualizados (referencian "49 passed" cuando hay 162 tests).

**Recomendación:** **Fusionar en `docs/quickstart.md`.** Crear un solo documento con secciones: instalación rápida, ejecución, verificación, pruebas, build APK. Actualizar el conteo de tests.

---

### 2.5. MEDIA: Metadocumentación fragmentada en 3 archivos

| Documento | Contenido |
|-----------|-----------|
| `documentation_inventory.md` | Inventario de documentos existentes. |
| `deprecated_docs_report.md` | Documentos obsoletos y recomendaciones. |
| `changelog_documentation.md` | Historial de cambios documentales. |

**Problema:** Los tres son "documentos sobre documentos". Podrían ser secciones de un solo documento de gobernanza documental.

**Recomendación:** **Fusionar en `docs/documentation_governance.md`** con secciones: inventario, obsoletos, changelog, reglas de escritura.

---

### 2.6. MEDIA: Plan de pruebas + Checklist QA

| Documento | Contenido |
|-----------|-----------|
| `testing_plan.md` | Estrategia de pruebas, suite actual, 60+ casos de prueba funcionales, pruebas de integración, responsive, negativas. |
| `qa_checklist.md` | 96 criterios de evaluación organizados en 12 categorías con resultados. |

**Problema:** No son redundantes en contenido, pero el checklist es efectivamente un subconjunto ejecutable del plan de pruebas. Juntos son difíciles de mantener sincronizados.

**Recomendación:** **Mantener separados pero vincularlos.** El plan de pruebas es la estrategia; el checklist es la herramienta de ejecución. Agregar referencia cruzada entre ambos.

---

### 2.7. BAJA: Informes QA en carpeta principal

| Documento | Contenido |
|-----------|-----------|
| `informe_qa_boxeo.md` | Informe QA del escenario boxeo (405 líneas). |
| `informe_qa_somatocarta.md` | Informe QA del escenario natación (177 líneas). |

**Problema:** No son redundantes entre sí, pero están mezclados con documentación técnica. Son artefactos de una sesión de prueba, no documentación del sistema.

**Recomendación:** **Mover a `docs/qa/`** para separar artefactos de prueba de documentación del sistema.

---

### 2.8. BAJA: AUDITORIA_SISTEMA.md — Documento híbrido obsoleto

| Campo | Detalle |
|-------|---------|
| **Contenido** | 406 líneas que mezclan: (1) plan de implementación de auditoría con código de ejemplo, (2) resumen de funcionalidades implementadas, (3) estado de dashboard, (4) próximos pasos. |
| **Problema** | El código de ejemplo ya fue implementado en `src/backend/audit.py`. Las secciones 2-4 son snapshots de un momento específico que ya no reflejan el estado actual. El documento no es ni especificación ni manual ni registro. |
| **Recomendación** | **Eliminar.** La auditoría ya está documentada en `modules.md` (módulo 17) y en `somatocarta_spec.md` (FR-018). Si se quiere conservar el historial, mover a `docs/qa/` como referencia histórica. |

---

### 2.9. BAJA: GUIA_GITHUB.md — Documento obsoleto

| Campo | Detalle |
|-------|---------|
| **Contenido** | Instrucciones genéricas para crear repositorio en GitHub. Referencia el nombre antiguo `FletSomatotipo_V1`. |
| **Problema** | El repositorio ya existe. Las instrucciones son triviales. El nombre del proyecto cambió. |
| **Recomendación** | **Eliminar.** |

---

## 3. Matriz de consolidación propuesta

| Acción | Archivos involucrados | Resultado |
|--------|----------------------|-----------|
| **Fusionar** | `especificacion_sdd_somatocarta.md` + `somatocarta_spec.md` | → `docs/specs/somatocarta_spec.md` (spec unificada) |
| **Fusionar** | `EJECUTAR_POWERSHELL.txt` + `comandos.txt` | → `docs/quickstart.md` |
| **Fusionar** | `documentation_inventory.md` + `deprecated_docs_report.md` + `changelog_documentation.md` | → `docs/documentation_governance.md` |
| **Eliminar** | `arquitectura.md` | Contenido ya está en `architecture.md` |
| **Eliminar** | `informe_final_sdd.md` | Duplicado de `informe_final_documentacion.md` |
| **Eliminar** | `AUDITORIA_SISTEMA.md` | Código ya implementado, snapshot obsoleto |
| **Eliminar** | `GUIA_GITHUB.md` | Obsoleto, nombre antiguo |
| **Mover** | `informe_qa_boxeo.md` + `informe_qa_somatocarta.md` | → `docs/qa/` |
| **Mover** | `informe_final_documentacion.md` | → `docs/qa/` (es un artefacto de sesión) |
| **Mantener** | `architecture.md` | Arquitectura técnica vigente |
| **Mantener** | `modules.md` | Módulos funcionales |
| **Mantener** | `formulas_somatotipo.md` | Referencia de cálculos |
| **Mantener** | `user_guide.md` | Guía de usuario |
| **Mantener** | `testing_plan.md` | Plan de pruebas |
| **Mantener** | `qa_checklist.md` | Checklist QA |
| **Mantener** | `publicacion.md` | Checklist de publicación |
| **Mantener** | `uploads.md` | Política de uploads |

---

## 4. Estructura resultante propuesta

Después de consolidación, `docs/` pasaría de **22 archivos** a **12 archivos** organizados así:

```text
docs/
├── specs/
│   └── somatocarta_spec.md          # Especificación unificada (SDD + Spec Kit)
├── qa/
│   ├── informe_qa_boxeo.md          # Informe QA escenario boxeo
│   ├── informe_qa_somatocarta.md    # Informe QA escenario natación
│   └── informe_final_documentacion.md # Informe de sesión documental
├── architecture.md                   # Arquitectura técnica
├── modules.md                        # Módulos funcionales
├── formulas_somatotipo.md            # Fórmulas y cálculos
├── user_guide.md                     # Guía de usuario
├── quickstart.md                     # Instalación y ejecución (fusión)
├── testing_plan.md                   # Plan de pruebas
├── qa_checklist.md                   # Checklist QA
├── documentation_governance.md       # Inventario + obsoletos + changelog (fusión)
├── publicacion.md                    # Checklist de publicación
└── uploads.md                        # Política de uploads
```

**Reducción:** 22 → 12 archivos (45% menos).

---

## 5. Contenido que se perdería en la fusión

| Documento origen | Contenido único a preservar | Destino |
|------------------|---------------------------|---------|
| `especificacion_sdd_somatocarta.md` | Sección 5.2 (vistas frontend), sección 7 (contratos API con JSON), sección 8 (flujos paso a paso), sección 9 (diseño de interfaz), sección 13 (evaluación arquitectónica), sección 14 (decisiones de diseño) | `specs/somatocarta_spec.md` |
| `arquitectura.md` | Nada relevante (ya está en `architecture.md`) | — |
| `comandos.txt` | Comando de build APK | `quickstart.md` |
| `EJECUTAR_POWERSHELL.txt` | Configuración de API_URL para red local | `quickstart.md` |
| `documentation_inventory.md` | Propuesta de estructura documental | `documentation_governance.md` |
| `deprecated_docs_report.md` | Tabla de obsoletos con recomendaciones | `documentation_governance.md` |
| `changelog_documentation.md` | Registro de cambios | `documentation_governance.md` |
| `AUDITORIA_SISTEMA.md` | Nada (código ya implementado) | — |

---

## 6. Documentos que NO deben tocarse

| Documento | Razón |
|-----------|-------|
| `formulas_somatotipo.md` | Contenido único, no duplicado, referencia crítica para validación clínica. |
| `publicacion.md` | Checklist operativo único. |
| `uploads.md` | Política operativa única. |
| `testing_plan.md` | Contenido complementario al checklist, no redundante. |
| `qa_checklist.md` | Herramienta de ejecución única. |
| `modules.md` | Descripción funcional única y detallada. |
| `architecture.md` | Arquitectura técnica vigente. |
| `user_guide.md` | Guía de usuario única. |

---

## 7. Prioridad de acciones

| Prioridad | Acción | Impacto | Esfuerzo |
|-----------|--------|---------|----------|
| **P1** | Eliminar `GUIA_GITHUB.md` | Reduce confusión | Mínimo |
| **P1** | Eliminar `informe_final_sdd.md` | Elimina duplicado exacto | Mínimo |
| **P2** | Eliminar `arquitectura.md` | Elimina redundancia con `architecture.md` | Mínimo |
| **P2** | Mover informes QA a `docs/qa/` | Organiza la carpeta | Bajo |
| **P3** | Fusionar especificaciones SDD | Elimina la mayor redundancia | Medio |
| **P3** | Fusionar guías de ejecución | Simplifica onboarding | Bajo |
| **P3** | Fusionar metadocumentación | Reduce fragmentación | Bajo |
| **P4** | Eliminar `AUDITORIA_SISTEMA.md` | Limpia documento obsoleto | Mínimo |

---

## 8. Riesgos de no actuar

1. **Desinformación:** Desarrolladores nuevos consultan documentos contradictorios o desactualizados.
2. **Doble mantenimiento:** Cuando cambie una funcionalidad, habrá que actualizar 2-3 documentos en vez de 1.
3. **Pérdida de credibilidad:** Una carpeta `docs/` con 22 archivos donde 10 son redundantes transmite desorganización.
4. **Especificación fragmentada:** La mitad del equipo consulta el SDD viejo y la otra mitad el Spec Kit nuevo.

---

*Informe generado el 15 de junio de 2026. No se modificó ningún archivo. Solo se analizó y documentó.*
