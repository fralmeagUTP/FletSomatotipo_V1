# Estado funcional

**Fecha de evaluación:** 30 de junio de 2026
**Estado estimado:** 95% funcional

El porcentaje es una estimación de preparación operativa, no cobertura de código. Se calcula sobre seis áreas ponderadas que suman 100 puntos.

| Área | Peso | Resultado | Evidencia |
|------|------|-----------|-----------|
| Flujos principales | 30 | 30 | El E2E recorre login, fotografía, CRUD, asignación, valoración, edición, PDF y eliminación ordenada. |
| Cálculos e integridad de datos | 25 | 25 | Las 76 valoraciones MySQL coinciden con la calculadora de referencia; claves foráneas y reglas `RESTRICT` verificadas. |
| Calidad automatizada | 15 | 15 | 236 pruebas y 7 subpruebas unitarias, de integración y E2E aprobadas. |
| Interfaz e informes | 15 | 14 | Shell responsive, PDFs optimizados y flujos Android validados en dispositivo; falta campaña visual completa en tablet/escritorio. |
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
- Android: login, Dashboard, logout, Atrás desde raíz y compartir PDF se validaron en un Xiaomi con Android 14.
- Calidad: cobertura global 74%; Historial (6%) y Dashboard (18%) requieren pruebas adicionales.
- CRUD móvil: deportistas en cuatro pasos y listados/formularios específicos para deportes, entidades y asignaciones.

## Trabajo restante

1. Migrar contraseñas heredadas a un hash seguro.
2. Exigir `SECRET_KEY` fuerte e implementar limitación de intentos de login.
3. Implementar administración de usuarios, roles y permisos.
4. Firmar el APK con keystore de release y reducir su tamaño.
5. Definir `WEB_ALLOWED_ORIGINS`, cabeceras HTTP defensivas, dominio, HTTPS y proxy WebSocket.
6. Excluir la API `/somatocarta/*` de Imunify360 Bot Protection para clientes Android/Python.
7. Elevar cobertura de Historial/Dashboard y completar validación visual en tablet/escritorio.
8. Obtener aprobación metodológica formal del protocolo antropométrico.

Los informes en `docs/qa/` conservan hallazgos históricos. Para el estado vigente prevalecen este documento y `docs/qa_checklist.md`.
