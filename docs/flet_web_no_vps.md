# Despliegue Flet Web sin VPS

## Arquitectura recomendada

La opción recomendada para el hosting compartido actual es separar únicamente la ejecución, no el código:

- **Backend FastAPI y MySQL:** permanecen en `https://nyquist.app/somatocarta` y en el cPanel actual.
- **Frontend Flet Web:** se ejecuta como servicio Python administrado en Render.
- **Dominio público Web:** `https://somatocarta.nyquist.app` mediante un registro DNS creado en cPanel.
- **Android:** continúa consumiendo `https://nyquist.app/somatocarta`; no requiere reconstrucción por este despliegue.

Esta distribución evita ejecutar Flet Web dentro de Passenger/WSGI, que no es adecuado para su conexión WebSocket persistente.

## Archivos preparados

- `render.yaml`: Blueprint del servicio Web.
- `requirements-web.txt`: dependencias exclusivas necesarias para el frontend.
- `web_main.py`: fábrica ASGI `create_web_app()`.

## Publicación inicial

1. Fusionar en `main` el PR que contiene Flet Web.
2. Crear una cuenta o iniciar sesión en Render.
3. Seleccionar **New > Blueprint**.
4. Conectar el repositorio `fralmeagUTP/FletSomatotipo_V1`.
5. Seleccionar la rama `main` y permitir que Render lea `render.yaml`.
6. Confirmar la variable:

```text
API_URL=https://nyquist.app/somatocarta
```

7. Esperar a que el health check `/` sea correcto.

El comando de producción configurado es:

```bash
python -m uvicorn web_main:create_web_app --factory --host 0.0.0.0 --port $PORT --proxy-headers
```

## Dominio `somatocarta.nyquist.app`

1. En Render, abrir el servicio `somatocarta-web`.
2. Agregar el dominio personalizado `somatocarta.nyquist.app`.
3. Render mostrará el hostname DNS de destino.
4. En el editor DNS de cPanel, crear el registro solicitado por Render, normalmente:

```text
Tipo: CNAME
Nombre: somatocarta
Destino: hostname-indicado-por-render
TTL: automático
```

5. Esperar la propagación DNS y la emisión automática del certificado HTTPS.

No cree un registro `A` inventado: use exactamente el destino entregado por Render.

## Ajuste del backend en cPanel

En el `.env` privado del backend agregue:

```text
WEB_ALLOWED_ORIGINS=https://somatocarta.nyquist.app
```

Reinicie la aplicación Passenger después de modificar el entorno. No cambie `API_URL` del APK ni mueva el backend existente.

## Actualizaciones posteriores

1. Fusionar los cambios a `main` en GitHub.
2. Render reconstruirá el frontend desde `requirements-web.txt`.
3. Actualizar el backend en cPanel solo cuando existan cambios bajo `src/backend/`, dependencias backend o migraciones.
4. No reemplazar `src/backend/static/uploads/` durante una actualización.

## Verificación

- Abrir `https://somatocarta.nyquist.app` desde escritorio y móvil.
- Iniciar sesión contra el backend existente.
- Verificar Dashboard y navegación.
- Crear o editar un deportista y probar fotografía.
- Abrir análisis individual y longitudinal.
- Descargar ambos PDF.
- Cerrar sesión y confirmar que solicita autenticación nuevamente.

Complete también `docs/flet_web_qa_checklist.md`.

## Consideraciones del plan administrado

Un plan que suspenda el servicio por inactividad puede causar una primera carga lenta y reconectar WebSocket. Para uso institucional continuo se recomienda un plan administrado sin suspensión. Esto sigue siendo una plataforma gestionada y no requiere administrar un VPS.
