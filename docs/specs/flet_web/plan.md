# Plan técnico: Somatocarta Flet Web

## Organización actual

- `main.py` contiene la entrada Flet, el login y el arranque de la navegación.
- `views/` contiene las nueve pantallas funcionales.
- `src/frontend/` centraliza tema, componentes, shell, navegación, activos, análisis visual y `ApiClient`.
- `src/backend/` contiene FastAPI, routers, servicios, dominio antropométrico y acceso MySQL.
- `assets/` contiene toda la identidad gráfica compartida.
- `tests/` valida backend, frontend, fórmulas, navegación y flujos E2E.

## Estrategia de reutilización

Se extraerá o parametrizará únicamente el arranque necesario para que la misma función Flet se ejecute en Android, escritorio y web. Las vistas, el shell, el tema, los activos y `ApiClient` seguirán siendo compartidos. Las diferencias de plataforma se concentrarán en configuración y utilidades pequeñas, evitando bifurcar las pantallas.

## Integración con FastAPI

La web consumirá `API_URL` mediante `ApiClient`, igual que Android. FastAPI seguirá siendo una aplicación y proceso separados. Para publicación web, FastAPI debe aceptar el origen HTTPS del frontend y servir sus endpoints bajo HTTPS.

## Endpoints consumidos

- `POST /auth/login` para JWT.
- `GET /dashboard/summary` para dashboard.
- `GET|POST /deportistas/` y `GET|PUT|DELETE /deportistas/{identi}`.
- `GET|POST /entidades/`, `PUT|DELETE /entidades/{nit}`.
- `GET|POST /deportes/`, `PUT|DELETE /deportes/{id}`.
- `GET|POST /asignaciones/`, `PUT|DELETE /asignaciones/{id}`.
- Endpoints de catálogos para formularios.
- Endpoints `/somatotipo/` para registro, detalle, historial, análisis y contrato de vista.
- `GET /somatotipo/{id}/pdf` y `GET /somatotipo/vista/deportista/{identi}/longitudinal/pdf`.
- `POST /files/upload` para fotografías.

## Separación Android y Web

- `main.py` seguirá siendo compatible con el empaquetado APK.
- Se añadirá un punto de entrada web explícito que invoque la misma función `main` con vista web.
- Una variable de entorno identificará el modo de ejecución cuando sea necesario.
- Las decisiones específicas de descarga o selección de archivos se encapsularán, sin duplicar lógica de negocio.
- No se modificarán `requirements-apk.txt`, identificadores Android ni configuración de empaquetado salvo necesidad comprobada.

## Identidad visual

La web importará `src/frontend/theme.py`, `src/frontend/components.py`, `src/frontend/app_shell.py` y los activos existentes. Los breakpoints del shell se ajustarán solo si las pruebas web detectan pérdidas de navegación o contenido. El resultado conservará barra lateral, menú móvil, tarjetas, botones, iconos, tipografía y colores existentes.

## Archivos previstos

### Crear

- `web_main.py`: entrada Flet Web.
- `start_web.bat`: ejecución local en Windows.
- `docs/specs/flet_web/spec.md`.
- `docs/specs/flet_web/plan.md`.
- `docs/specs/flet_web/tasks.md`.
- `docs/flet_web_deployment.md`.
- `docs/flet_web_qa_checklist.md`.
- Pruebas específicas del arranque/configuración web si no encajan en archivos existentes.

### Modificar según validación

- `main.py`: metadatos o configuración compartida mínima.
- `app_config.py`: modo de ejecución y configuración web segura.
- `src/frontend/app_shell.py`: respuesta a cambios de tamaño si es necesario.
- `src/frontend/api_client.py`: descarga compatible con navegador si el flujo actual escribe solo al disco local.
- Vistas que invoquen selección, carga o descarga de archivos.
- `README.md` y documentación relacionada.

## Estrategia de pruebas

1. Pruebas unitarias del punto de entrada web y configuración por entorno.
2. Pruebas existentes de login, navegación, shell móvil y vistas compartidas.
3. Prueba de inicio del servidor Flet Web y respuesta HTTP local.
4. Pruebas manuales en anchos de escritorio, tablet y móvil usando el checklist.
5. Suite completa de `pytest` para detectar regresiones Android/backend.
6. Verificación de que `main.py` continúa importando y ejecutando la entrada usada por el APK.
7. Verificación ASGI de que cada archivo de `assets/` se entrega sin cambios.
8. Captura real de login responsive en Chrome y revisión manual de vistas autenticadas antes de producción.
