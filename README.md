# Somatocarta

Aplicación Flet + FastAPI para gestión de deportistas, valoración corporal y consulta de historial de somatotipo.

## Arranque rápido

1. Crear/activar entorno e instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

2. Ejecutar backend:

```powershell
.\start_backend.bat
```

3. Ejecutar frontend en otra terminal:

```powershell
.\start_frontend.bat
```

## Configuración

Crear `.env` a partir de `.env.example`.

Variables principales:

- `API_URL`: URL consumida por el frontend. Por defecto: `http://127.0.0.1:8085`.
- Variables de base de datos usadas por `src/backend/database.py`.

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Preflight antes de publicar:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\preflight_publicacion.ps1
```

Resultado actual esperado:

```text
49 passed
```

## Documentación

- Arquitectura: `docs/arquitectura.md`
- Publicación: `docs/publicacion.md`
- Ejecución detallada: `EJECUTAR_POWERSHELL.txt`
- Comandos rápidos: `comandos.txt`

## Estructura

```text
main.py
views/
src/frontend/
src/backend/routers/
src/backend/schemas/
src/backend/services/
tests/
```

## Notas de mantenimiento

- No guardar secretos en Git; usar `.env`.
- No usar `requests` directamente en vistas; usar `src/frontend/api_client.py`.
- Mantener routers backend delgados; mover lógica a `src/backend/services/`.
- Antes de publicar, revisar archivos no relacionados como backups `.zip` e imágenes en `src/backend/static/uploads/`.
