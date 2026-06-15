# Gobernanza documental — Somatocarta v1.1.7

**Fusionado de:** `documentation_inventory.md` + `deprecated_docs_report.md` + `changelog_documentation.md`
**Fecha:** 15 de junio de 2026

---

## 1. Inventario documental vigente

### 1.1 Estructura actual de `docs/`

```text
docs/
├── specs/
│   └── somatocarta_spec.md          # Especificación unificada (SDD + Spec Kit)
├── qa/
│   ├── informe_qa_boxeo.md          # Informe QA escenario boxeo
│   ├── informe_qa_somatocarta.md    # Informe QA escenario natación
│   ├── informe_final_documentacion.md # Informe de sesión documental
│   └── informe_redundancias.md      # Análisis de redundancias
├── architecture.md                   # Arquitectura técnica
├── modules.md                        # Módulos funcionales
├── formulas_somatotipo.md            # Fórmulas y cálculos
├── user_guide.md                     # Guía de usuario
├── quickstart.md                     # Instalación y ejecución
├── testing_plan.md                   # Plan de pruebas
├── qa_checklist.md                   # Checklist QA
├── documentation_governance.md       # Este documento
├── publicacion.md                    # Checklist de publicación
└── uploads.md                        # Política de uploads
```

### 1.2 Documentos en la raíz del proyecto

| Archivo | Tipo | Estado | Acción |
|---------|------|--------|--------|
| `README.md` | Guía principal | Actualizado | Mantener |
| `requirements.txt` | Dependencias | Actualizado | Mantener |
| `requirements-apk.txt` | Dependencias APK | Actualizado | Mantener |
| `Respaldo_20251214_0840.zip` | Backup | No relacionado | Recomendar eliminación |
| `Respaldo_v1.1.1.zip` | Backup | No relacionado | Recomendar eliminación |

### 1.3 Documentos de referencia (no .md)

| Archivo | Tipo | Acción |
|---------|------|--------|
| `comandos.txt` (raíz) | Referencia rápida | Mantener como respaldo |
| `EJECUTAR_POWERSHELL.txt` (raíz) | Guía de ejecución | Mantener como respaldo |

---

## 2. Documentos eliminados

Los siguientes documentos fueron eliminados el 15 de junio de 2026 durante la consolidación documental:

| Documento | Motivo de eliminación |
|-----------|----------------------|
| `docs/GUIA_GITHUB.md` | Instrucciones genéricas obsoletas. Nombre antiguo del proyecto. |
| `docs/informe_final_sdd.md` | Duplicado de `informe_final_documentacion.md`. |
| `docs/AUDITORIA_SISTEMA.md` | Código de ejemplo ya implementado. Snapshot obsoleto. |
| `docs/arquitectura.md` | Redundante con `docs/architecture.md`. |
| `docs/especificacion_sdd_somatocarta.md` | Fusionado en `docs/specs/somatocarta_spec.md`. |
| `docs/EJECUTAR_POWERSHELL.txt` | Fusionado en `docs/quickstart.md`. |
| `docs/comandos.txt` | Fusionado en `docs/quickstart.md`. |

---

## 3. Documentos movidos

| Documento | Origen | Destino |
|-----------|--------|---------|
| `informe_qa_boxeo.md` | `docs/` | `docs/qa/` |
| `informe_qa_somatocarta.md` | `docs/` | `docs/qa/` |
| `informe_final_documentacion.md` | `docs/` | `docs/qa/` |
| `informe_redundancias.md` | `docs/` | `docs/qa/` |
| `somatocarta_spec.md` | `docs/` | `docs/specs/` |

---

## 4. Documentos vigentes que no deben modificarse

| Documento | Razón |
|-----------|-------|
| `docs/formulas_somatotipo.md` | Contenido único, no duplicado. Referencia crítica para validación clínica. |
| `docs/publicacion.md` | Checklist operativo vigente y útil. |
| `docs/uploads.md` | Política operativa vigente. |
| `docs/testing_plan.md` | Contenido complementario al checklist, no redundante. |
| `docs/qa_checklist.md` | Herramienta de ejecución única. |
| `docs/modules.md` | Descripción funcional única y detallada. |
| `docs/architecture.md` | Arquitectura técnica vigente. |
| `docs/user_guide.md` | Guía de usuario única. |
| `docs/specs/somatocarta_spec.md` | Especificación unificada. Fuente de verdad. |

---

## 5. Reglas de escritura documental

- Clara, técnica, organizada.
- Útil para desarrolladores y usuarios académicos.
- Coherente con SDD y el estado real de la app.
- Escrita en español.
- Sin afirmaciones no verificadas.
- Sin prometer funcionalidades que no existen.
- Cuando no se esté seguro, escribir: *Pendiente de confirmar en código.*

---

## 6. Estructura documental por pilares

1. **Especificación** (`docs/specs/`): Spec Kit, requisitos, modelo de dominio, contratos API.
2. **Técnica** (`docs/`): Arquitectura, módulos, fórmulas.
3. **Operativa** (`docs/`): Guía de usuario, instalación rápida, publicación, uploads.
4. **Calidad** (`docs/`): Plan de pruebas, checklist QA, informes QA.

---

## 7. Changelog documental

### 2026-06-15 — Consolidación documental

**Acciones ejecutadas:**

- Eliminados 7 documentos obsoletos o redundantes.
- Movidos 5 documentos a subcarpetas organizadas.
- Fusionadas 2 especificaciones SDD en `docs/specs/somatocarta_spec.md`.
- Fusionadas 2 guías de ejecución en `docs/quickstart.md`.
- Fusionados 3 metadocumentos en `docs/documentation_governance.md` (este archivo).

**Resultado:** Reducción de 22 a 12 documentos en `docs/` (45% menos).

**Documentos creados:**

| Documento | Propósito |
|-----------|-----------|
| `docs/specs/somatocarta_spec.md` | Especificación unificada (SDD + Spec Kit + apéndices) |
| `docs/quickstart.md` | Guía rápida de instalación y ejecución |
| `docs/documentation_governance.md` | Gobernanza documental unificada |

**Documentos actualizados:**

| Documento | Cambios |
|-----------|---------|
| `README.md` | Reescrito con todos los módulos, versión, estructura, tecnologías |
| `docs/architecture.md` | Actualizado con routers, servicios, auditoría, endpoints |

**Pendientes:**

- Confirmar eliminación de archivos ZIP de respaldo en la raíz.
- Documentar definición SQL de `CDRVistaValoracionCorporal`.
- Agregar casos de prueba clínicos conocidos para validar cálculos.
- Validar con el equipo si `comandos.txt` y `EJECUTAR_POWERSHELL.txt` de la raíz se eliminan.

---

*Este documento se actualiza con cada revisión documental.*
