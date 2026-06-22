# Estado funcional

**Fecha de evaluación:** 21 de junio de 2026  
**Estado estimado:** 94% funcional

El porcentaje es una estimación de preparación operativa, no cobertura de código. Se calcula sobre seis áreas ponderadas que suman 100 puntos.

| Área | Peso | Resultado | Evidencia |
|------|------|-----------|-----------|
| Flujos principales | 30 | 30 | El E2E recorre login, fotografía, CRUD, asignación, valoración, edición, PDF y eliminación ordenada. |
| Cálculos e integridad de datos | 25 | 25 | Las 76 valoraciones MySQL coinciden con la calculadora de referencia; claves foráneas y reglas `RESTRICT` verificadas. |
| Calidad automatizada | 15 | 15 | 183 pruebas y 3 subpruebas unitarias, de integración y E2E aprobadas. |
| Interfaz e informes | 15 | 14 | Shell responsive dinámico y PDFs variables optimizados; falta validación visual en dispositivos reales. |
| Seguridad y accesos | 10 | 5 | JWT y auditoría activos; faltan hash de contraseñas, roles administrativos y política CORS explícita. |
| Operación y documentación | 5 | 5 | Backend, health check, migraciones y procedimientos documentados. |
| **Total** | **100** | **94** | **La aplicación supera el objetivo del 90% funcional.** |

## Validaciones cerradas

- Migraciones `002` y `003`: integridad referencial y política `RESTRICT` activas.
- Migración `004`: unidades históricas y vistas antropométricas corregidas.
- Verificación MySQL: 76 valoraciones, 0 diferencias.
- Backend: `GET /health` devuelve `status=ok` y `database=connected`.
- Fórmulas: Yuhasz es el método principal y Faulkner la referencia comparativa.
- Responsive: sidebar y menú móvil cambian dinámicamente al redimensionar sin perder el layout interno de la vista.
- E2E: flujo crítico completo validado sobre FastAPI y SQLite aislado.
- PDF: contenido distinto por deportista y generación principal inferior a 1 segundo en pruebas.

## Trabajo restante

1. Migrar contraseñas heredadas a un hash seguro.
2. Implementar administración de usuarios, roles y permisos.
3. Definir CORS por ambiente de despliegue.
4. Ejecutar validación visual en dispositivos reales: móvil, tablet y escritorio.
5. Obtener aprobación metodológica formal del protocolo antropométrico.

Los informes en `docs/qa/` conservan hallazgos históricos. Para el estado vigente prevalecen este documento y `docs/qa_checklist.md`.
