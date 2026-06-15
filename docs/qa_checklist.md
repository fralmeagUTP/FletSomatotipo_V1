# Checklist de evaluación QA — Somatocarta v1.1.7

**Fecha:** 15 de junio de 2026

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
| 2.6 | Muestra actividad reciente | ⚠️ | No siempre refleja las más nuevas |
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
| 3.13 | Carga de fotografía funciona | 🔲 | No evaluado visualmente |
| 3.14 | Deportista con valoraciones se elimina sin restricción | ❌ | Riesgo de integridad |

## 4. CRUD Entidades

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 4.1 | Crear entidad | ✅ | |
| 4.2 | Listar entidades | ✅ | |
| 4.3 | Buscar entidad | ✅ | |
| 4.4 | Editar entidad | ✅ | |
| 4.5 | Eliminar entidad | ✅ | |
| 4.6 | Rechaza NIT duplicado | ✅ | Error 400 |
| 4.7 | Entidad con asignaciones se elimina sin restricción | ❌ | Riesgo de integridad |

## 5. CRUD Deportes

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 5.1 | Crear deporte | ✅ | |
| 5.2 | Listar deportes | ✅ | |
| 5.3 | Buscar deporte | ✅ | |
| 5.4 | Editar deporte | ✅ | |
| 5.5 | Eliminar deporte | ✅ | |
| 5.6 | Rechaza deporte duplicado | ❌ | Permite duplicados (200) |
| 5.7 | Deporte con asignaciones se elimina sin restricción | ❌ | Riesgo de integridad |

## 6. CRUD Asignaciones

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 6.1 | Crear asignación | ✅ | |
| 6.2 | Listar asignaciones | ✅ | |
| 6.3 | Editar asignación | ✅ | |
| 6.4 | Eliminar asignación | ✅ | |
| 6.5 | Valida que deportista exista | ✅ | Error 422 |
| 6.6 | Rechaza asignación duplicada | ❌ | Permite duplicados (200) |

## 7. Valoración Corporal

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 7.1 | Crear valoración con 1 toma | ✅ | |
| 7.2 | Crear valoración con 3 tomas | ✅ | |
| 7.3 | Agregar toma adicional a valoración existente | ✅ | |
| 7.4 | Editar detalle de valoración almacenada | ⚠️ | Endpoint inconsistente |
| 7.5 | Eliminar detalle individual | 🔲 | No evaluado a fondo |
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
| 8.8 | Mesomorfismo muestra valores coherentes | ❌ | Valores negativos para atletas |
| 8.9 | Peso óseo muestra valores coherentes | ❌ | 0.35-0.50 kg (irreal) |
| 8.10 | Textos de escala son coherentes | ❌ | Texto corrupto en ectomorfismo |

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
| 10.8 | PDFs varían entre deportistas | ⚠️ | Todos tienen el mismo tamaño exacto |

## 11. Responsive

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 11.1 | Login en móvil | 🔲 | No evaluado visualmente |
| 11.2 | Dashboard en móvil | 🔲 | No evaluado visualmente |
| 11.3 | Historial master-detail en escritorio | 🔲 | No evaluado visualmente |
| 11.4 | Historial toggle en móvil | 🔲 | No evaluado visualmente |
| 11.5 | Sin scroll horizontal no deseado | 🔲 | No evaluado visualmente |

## 12. Seguridad

| # | Criterio | Estado | Observaciones |
|---|----------|--------|---------------|
| 12.1 | Contraseñas en texto plano | ❌ | Riesgo de seguridad |
| 12.2 | SECRET_KEY configurable por .env | ✅ | |
| 12.3 | Token JWT con expiración | ✅ | 15 min |
| 12.4 | Auditoría de operaciones CRUD | ✅ | |
| 12.5 | Control de roles y permisos | ❌ | No implementado |
| 12.6 | CORS configurado | ❌ | No configurado explícitamente |

---

## Resumen

| Categoría | Total | Pass | Fail | Parcial | No evaluado |
|-----------|-------|------|------|---------|-------------|
| Autenticación | 8 | 8 | 0 | 0 | 0 |
| Dashboard | 8 | 7 | 0 | 1 | 0 |
| CRUD Deportistas | 14 | 12 | 1 | 0 | 1 |
| CRUD Entidades | 7 | 6 | 1 | 0 | 0 |
| CRUD Deportes | 7 | 5 | 2 | 0 | 0 |
| CRUD Asignaciones | 6 | 5 | 1 | 0 | 0 |
| Valoración Corporal | 11 | 10 | 0 | 1 | 0 |
| Análisis Individual | 10 | 7 | 3 | 0 | 0 |
| Análisis Longitudinal | 6 | 6 | 0 | 0 | 0 |
| Informes PDF | 8 | 7 | 0 | 1 | 0 |
| Responsive | 5 | 0 | 0 | 0 | 5 |
| Seguridad | 6 | 3 | 3 | 0 | 0 |
| **Total** | **96** | **76** | **11** | **3** | **6** |

**Tasa de aprobación:** 79.2% (76/96)
**Tasa de fallo:** 11.5% (11/96)

---

*Checklist basado en pruebas ejecutadas el 15 de junio de 2026. Las pruebas responsive requieren evaluación visual manual.*
