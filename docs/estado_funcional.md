# Estado funcional

**Fecha de evaluación:** 29 de junio de 2026
**Estado estimado:** 95% funcional

El porcentaje es una estimación de preparación operativa, no cobertura de código. Se calcula sobre seis áreas ponderadas que suman 100 puntos.

| Área | Peso | Resultado | Evidencia |
|------|------|-----------|-----------|
| Flujos principales | 30 | 30 | El E2E recorre login, fotografía, CRUD, asignación, valoración, edición, PDF y eliminación ordenada. |
| Cálculos e integridad de datos | 25 | 25 | Las 76 valoraciones MySQL coinciden con la calculadora de referencia; claves foráneas y reglas `RESTRICT` verificadas. |
| Calidad automatizada | 15 | 15 | 227 pruebas y 7 subpruebas unitarias, de integración y E2E aprobadas. |
| Interfaz e informes | 15 | 14 | Shell responsive dinámico y PDFs variables optimizados; falta validación visual en dispositivos reales. |
| Seguridad y accesos | 10 | 6 | JWT, auditoría y CORS configurable activos; faltan hash de contraseñas, roles administrativos y fijar orígenes productivos. |
| Operación y documentación | 5 | 5 | Backend, health check, migraciones y procedimientos documentados. |
| **Total** | **100** | **95** | **La aplicación supera el objetivo del 90% funcional.** |

## Validaciones cerradas

- Migraciones `002` y `003`: integridad referencial y política `RESTRICT` activas.
- Migración `004`: unidades históricas y vistas antropométricas corregidas.
- Verificación MySQL: 76 valoraciones, 0 diferencias.
- Backend: `GET /health` devuelve `status=ok` y `database=connected`.
- Fórmulas: Yuhasz es el método principal y Faulkner la referencia comparativa.
- Responsive: Web y Android comparten reglas de negocio, pero usan layouts separados; los CRUD móviles y el análisis longitudinal tienen composición propia.
- E2E: flujo crítico completo validado sobre FastAPI y SQLite aislado.
- PDF: contenido distinto por deportista y generación principal inferior a 1 segundo en pruebas.
- Flet Web: entrada local y fábrica ASGI funcionales; todos los assets móviles se sirven desde Web y el login fue validado en Chrome a 390 × 844 px.
- Dashboard: accesos rápidos usan iconos Material vectoriales uniformes en Web y Android.
- Android: login permite revelar contraseña; encabezado permite cerrar sesión; PDF individual y longitudinal se pueden compartir con aplicaciones instaladas.
- CRUD móvil: deportistas en cuatro pasos y listados/formularios específicos para deportes, entidades y asignaciones.

## Trabajo restante

1. Migrar contraseñas heredadas a un hash seguro.
2. Implementar administración de usuarios, roles y permisos.
3. Definir el valor productivo de `WEB_ALLOWED_ORIGINS`, dominio, HTTPS y proxy WebSocket.
4. Excluir la API `/somatocarta/*` de Imunify360 Bot Protection para clientes Android/Python.
5. Ejecutar validación visual en dispositivos reales: móvil, tablet y escritorio.
6. Obtener aprobación metodológica formal del protocolo antropométrico.

Los informes en `docs/qa/` conservan hallazgos históricos. Para el estado vigente prevalecen este documento y `docs/qa_checklist.md`.
