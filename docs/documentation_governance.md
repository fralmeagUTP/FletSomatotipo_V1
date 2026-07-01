# Gobernanza documental — Somatocarta v1.2.11

**Origen:** consolidación de inventario, reporte de obsolescencia y changelog histórico.
**Fecha de actualización:** 30 de junio de 2026

---

## 1. Inventario documental vigente

### 1.1 Estructura actual de `docs/`

```text
docs/
├── specs/
│   ├── somatocarta_spec.md          # Especificación unificada (SDD + Spec Kit)
│   └── flet_web/                    # Especificación, plan y tareas Web
├── qa/
│   ├── informe_qa_boxeo.md          # Evidencia QA histórica
│   ├── informe_qa_somatocarta.md    # Evidencia QA histórica
│   ├── informe_final_documentacion.md # Informe histórico de consolidación
│   └── informe_redundancias.md      # Inventario histórico
├── architecture.md                   # Arquitectura técnica
├── modules.md                        # Módulos funcionales
├── formulas_somatotipo.md            # Fórmulas y cálculos
├── integridad_referencial.md          # Política RESTRICT y migraciones
├── estado_funcional.md                # Estado vigente y porcentaje ponderado
├── user_guide.md                     # Guía de usuario
├── quickstart.md                     # Instalación y ejecución
├── testing_plan.md                   # Plan de pruebas
├── qa_checklist.md                   # Checklist QA
├── documentation_governance.md       # Este documento
├── changelog_documentation.md         # Registro cronológico de cambios
├── publicacion.md                    # Checklist de publicación
├── uploads.md                        # Política de uploads
├── flet_web_deployment.md            # Ejecución y despliegue Web
├── flet_web_no_vps.md                 # Despliegue administrado con backend cPanel
└── flet_web_qa_checklist.md           # Checklist QA Web
```

### 1.2 Documentos en la raíz del proyecto

| Archivo | Tipo | Estado | Acción |
|---------|------|--------|--------|
| `README.md` | Guía principal | Actualizado | Mantener |
| `requirements.txt` | Dependencias | Actualizado | Mantener |
| `requirements-apk.txt` | Dependencias APK | Actualizado | Mantener |

### 1.3 Documentos de referencia (no .md)

Las instrucciones operativas se concentran en `README.md`, `docs/quickstart.md` y `docs/publicacion.md`. No existen guías `.txt` vigentes en la raíz.

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

Los documentos sí pueden actualizarse cuando cambia el código; la tabla significa que no deben eliminarse ni fusionarse sin una revisión documental explícita.

Los informes dentro de `docs/qa/` son evidencia histórica y no representan el estado vigente. El estado actual se consulta en `docs/estado_funcional.md` y `docs/qa_checklist.md`.

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
- Confirmar periódicamente que no reaparezcan guías operativas duplicadas en la raíz.

### 2026-06-21 — Actualización integral

- Estado funcional ponderado establecido en 94%.
- Fórmulas y 76 valoraciones MySQL verificadas sin diferencias.
- Integridad referencial `RESTRICT`, duplicados y confirmaciones documentados como resueltos.
- Responsive dinámico, E2E crítico y PDFs variables/optimizados incorporados.
- Suite actualizada a 206 pruebas y 7 subpruebas.
- Informes QA antiguos etiquetados como históricos y credenciales retiradas.
- Creado `docs/changelog_documentation.md` como registro independiente.

### 2026-06-22 — Frontend Flet Web y paridad visual

- Añadida especificación Spec Kit específica para Flet Web.
- Documentados entrada local, fábrica ASGI, variables, CORS, HTTPS y proxy WebSocket.
- Incorporados checklist QA Web y validación de assets compartidos Android/Web.
- Dashboard documentado con iconografía Material vectorial en lugar de miniaturas raster.
- Estado ponderado actualizado a 95% y suite vigente a 206 pruebas y 7 subpruebas.

### 2026-06-29 — Release v1.2.5 y separación Web/Android

- Actualizadas versión, arquitectura, módulos, guía de usuario, pruebas, QA, despliegue y publicación.
- Documentados CRUD móviles específicos, análisis longitudinal móvil completo y layouts Web independientes.
- Documentados revelado de contraseña, logout superior y orden institucional de logotipos.
- Documentada entrega PDF por plataforma y compartir Android mediante `ACTION_SEND`/`FileProvider`.
- Registrada la exclusión requerida de Imunify360 Bot Protection para la API pública.
- Generado build Android universal `1.2.5` con `versionCode=12`, firma de pruebas v2 verificada y SHA-256 `68AFB85A48A6475653F3A0D55A90F97936BF283953A2BD597538DBE7A4E38B8F`.
- Suite final verificada en esa entrega: 227 pruebas y 7 subpruebas aprobadas.

### 2026-06-30 — Release interna v1.2.11 y evaluación integral

- Documentadas la pila Atrás de Android, cierre desde raíz, logout seguro, búsqueda unificada y acciones CRUD móviles.
- Registrado APK `v1.2.11`, `versionCode=22`, SHA-256 `97E4359BD28C8D2D9E38990086D4F8FE86BC95BB830FDB0252160A558149FE31`.
- Suite vigente: 244 pruebas, 7 subpruebas y cobertura global del 74%.
- Reforzada la separación visual por plataforma: una página Web estrecha no activa las composiciones exclusivas del APK.
- Creado `docs/qa/informe_pruebas_integrales_2026-06-30.md` con dictamen: apto para pruebas internas, no aprobado para publicación hasta corregir seguridad y firma.

---

*Este documento se actualiza con cada revisión documental.*
