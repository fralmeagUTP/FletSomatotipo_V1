# Checklist de evaluación QA — Somatocarta v1.2.1

**Fecha:** 22 de junio de 2026

---

## Instrucciones

Marque cada ítem con:
- ✅ Pass
- ❌ Fail
- ⚠️ Parcial
- 🔲 No evaluado

---

## 1. Autenticación

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 1.1 | Login con credenciales válidas funciona | ✅ | Token JWT generado |
| 1.2 | Login con usuario incorrecto retorna 401 | ✅ | |
| 1.3 | Login con contraseña incorrecta retorna 401 | ✅ | |
| 1.4 | Login con campos vacíos retorna error | ✅ | |
| 1.5 | Endpoints protegidos sin token retornan 401 | ✅ | |
| 1.6 | Token inválido retorna 401 | ✅ | |
| 1.7 | Cerrar sesión limpia el token | ✅ | |
| 1.8 | Auditoría registra login exitoso y fallido | ✅ | |

## 2. Dashboard

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 2.1 | Muestra total de deportistas | ✅ | |
| 2.2 | Muestra total de valoraciones | ✅ | |
| 2.3 | Muestra total de deportes | ✅ | |
| 2.4 | Muestra total de entidades | ✅ | |
| 2.5 | Muestra total de asignaciones | ✅ | |
| 2.6 | Accesos rápidos usan iconos vectoriales legibles | ✅ | Iconos Material compartidos por Web y Android |
| 2.7 | Muestra estado del contrato de vista SQL | ✅ | |
| 2.8 | Navegación a módulos funciona | ✅ | |

## 3. CRUD Deportistas

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 3.1 | Crear deportista con datos válidos | ✅ | |
| 3.2 | Listar deportistas con paginación | ✅ | |
| 3.3 | Buscar deportista por nombre | ✅ | |
| 3.4 | Buscar deportista por ID | ✅ | |
| 3.5 | Consultar detalle de deportista | ✅ | |
| 3.6 | Editar deportista | ✅ | |
| 3.7 | Eliminar deportista | ✅ | |
| 3.8 | Rechaza ID duplicado | ✅ | Error 400 |
| 3.9 | Rechaza sexo inválido | ✅ | Error 422 |
| 3.10 | Rechaza email inválido | ✅ | Error 422 |
| 3.11 | Rechaza fecha de nacimiento futura | ✅ | Error 422 |
| 3.12 | Rechaza campos obligatorios vacíos | ✅ | Error 422 |
| 3.13 | Carga de fotografía funciona | ✅ | Cubierta por flujo E2E autenticado |
| 3.14 | Bloquea eliminar deportista con asignaciones o valoraciones | ✅ | Error 409 |

## 4. CRUD Entidades

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 4.1 | Crear entidad | ✅ | |
| 4.2 | Listar entidades | ✅ | |
| 4.3 | Buscar entidad | ✅ | |
| 4.4 | Editar entidad | ✅ | |
| 4.5 | Eliminar entidad | ✅ | |
| 4.6 | Rechaza NIT duplicado | ✅ | Error 400 |
| 4.7 | Bloquea eliminar entidad con asignaciones | ✅ | Error 409 |

## 5. CRUD Deportes

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 5.1 | Crear deporte | ✅ | |
| 5.2 | Listar deportes | ✅ | |
| 5.3 | Buscar deporte | ✅ | |
| 5.4 | Editar deporte | ✅ | |
| 5.5 | Eliminar deporte | ✅ | |
| 5.6 | Rechaza deporte duplicado | ✅ | Error 409 |
| 5.7 | Bloquea eliminar deporte con asignaciones | ✅ | Error 409 |

## 6. CRUD Asignaciones

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 6.1 | Crear asignación | ✅ | |
| 6.2 | Listar asignaciones | ✅ | |
| 6.3 | Editar asignación | ✅ | |
| 6.4 | Eliminar asignación | ✅ | |
| 6.5 | Valida que deportista exista | ✅ | Error 422 |
| 6.6 | Rechaza asignación duplicada | ✅ | Error 409 |

## 7. Valoración Corporal

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 7.1 | Crear valoración con 1 toma | ✅ | |
| 7.2 | Crear valoración con 3 tomas | ✅ | |
| 7.3 | Agregar toma adicional a valoración existente | ✅ | |
| 7.4 | Editar detalle de valoración almacenada | ✅ | Cubierta por flujo E2E autenticado |
| 7.5 | Eliminar detalle individual | ✅ | Cubierta por pruebas de ruta e integración |
| 7.6 | Eliminar valoración completa | ✅ | |
| 7.7 | Rechaza valores fuera de rango | ✅ | Error 422 |
| 7.8 | Rechaza valoración sin detalles | ✅ | Error 422 |
| 7.9 | Rechaza fecha de medición futura | ✅ | Error 422 |
| 7.10 | Rechaza fecha duplicada por deportista | ✅ | Constraint único |
| 7.11 | Cargar valoración almacenada | ✅ | |

## 8. Análisis Individual

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 8.1 | Historial muestra valoraciones del deportista | ✅ | |
| 8.2 | Detalle muestra medidas antropométricas | ✅ | |
| 8.3 | Detalle muestra composición corporal | ✅ | |
| 8.4 | Detalle muestra IMC y estado | ✅ | |
| 8.5 | Detalle muestra complexión física | ✅ | |
| 8.6 | Detalle muestra somatotipo | ✅ | |
| 8.7 | Somatocarta ubica al deportista | ✅ | |
| 8.8 | Mesomorfismo muestra valores coherentes | ✅ | Fórmula y unidades corregidas; verificación MySQL completa |
| 8.9 | Peso óseo muestra valores coherentes | ✅ | Diámetros normalizados a mm y fórmula corregida |
| 8.10 | Textos de escala son coherentes | ✅ | Texto de ectomorfismo corregido por migración `004` |

## 9. Análisis Longitudinal

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 9.1 | Muestra gráficos de tendencia | ✅ | |
| 9.2 | Muestra tarjetas de cambio | ✅ | |
| 9.3 | Somatocarta longitudinal con trayectoria | ✅ | |
| 9.4 | Comparación de métodos de grasa | ✅ | |
| 9.5 | Tabla histórica completa | ✅ | |
| 9.6 | Requiere mínimo 2 valoraciones | ✅ | |

## 10. Informes PDF

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 10.1 | PDF individual se genera y descarga | ✅ | |
| 10.2 | PDF individual es válido (firma %PDF) | ✅ | |
| 10.3 | PDF individual contiene datos del deportista | ✅ | |
| 10.4 | PDF individual contiene métricas | ✅ | |
| 10.5 | PDF longitudinal se genera y descarga | ✅ | |
| 10.6 | PDF longitudinal es válido | ✅ | |
| 10.7 | PDF longitudinal contiene datos correctos | ✅ | |
| 10.8 | PDFs varían entre deportistas | ✅ | Identidad, métricas y bytes comparados automáticamente |

## 11. Responsive

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 11.1 | Login en navegador móvil | ✅ | Validado en Chrome a 390 × 844 px con assets completos |
| 11.2 | Dashboard en móvil | 🔲 | No evaluado visualmente |
| 11.3 | Historial master-detail en escritorio | 🔲 | No evaluado visualmente |
| 11.4 | Historial toggle en móvil | 🔲 | No evaluado visualmente |
| 11.5 | Sin scroll horizontal no deseado | 🔲 | No evaluado visualmente |

## 12. Seguridad

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 12.1 | Contraseñas en texto plano | ❌ | Riesgo de seguridad |
| 12.2 | SECRET_KEY configurable por .env | ✅ | |
| 12.3 | Token JWT con expiración | ✅ | 30 min por defecto, configurable por entorno |
| 12.4 | Auditoría de operaciones CRUD | ✅ | |
| 12.5 | Control de roles y permisos | ❌ | No implementado |
| 12.6 | CORS configurable por entorno | ✅ | `WEB_ALLOWED_ORIGINS`; falta definir dominio productivo |

---

## Resumen

| Categoría | Total | Pass | Fail | Parcial | No evaluado |
|-----------|-------|------|------|---------|-------------|
| Autenticación | 8 | 8 | 0 | 0 | 0 |
| Dashboard | 8 | 8 | 0 | 0 | 0 |
| CRUD Deportistas | 14 | 14 | 0 | 0 | 0 |
| CRUD Entidades | 7 | 7 | 0 | 0 | 0 |
| CRUD Deportes | 7 | 7 | 0 | 0 | 0 |
| CRUD Asignaciones | 6 | 6 | 0 | 0 | 0 |
| Valoración Corporal | 11 | 11 | 0 | 0 | 0 |
| Análisis Individual | 10 | 10 | 0 | 0 | 0 |
| Análisis Longitudinal | 6 | 6 | 0 | 0 | 0 |
| Informes PDF | 8 | 8 | 0 | 0 | 0 |
| Responsive | 5 | 1 | 0 | 0 | 4 |
| Seguridad | 6 | 4 | 2 | 0 | 0 |
| **Total** | **96** | **90** | **2** | **0** | **4** |

**Tasa de aprobación:** 93.8% (90/96)
**Tasa de fallo:** 2.1% (2/96)

---

*Checklist actualizado el 22 de junio de 2026. La matriz detallada para navegador está en `docs/flet_web_qa_checklist.md`; las vistas autenticadas responsive aún requieren evaluación visual manual. El porcentaje funcional ponderado se documenta en `docs/estado_funcional.md`.*
