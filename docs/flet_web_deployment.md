# Ejecución y despliegue de Flet Web

> Para el hosting compartido actual, use la arquitectura administrada descrita en `docs/flet_web_no_vps.md`. No requiere VPS y mantiene FastAPI/MySQL en cPanel.

## Arquitectura

Flet Web y FastAPI son procesos separados:

- Flet Web sirve la interfaz y mantiene la sesión de cada navegador.
- `ApiClient` realiza las solicitudes autenticadas a FastAPI usando `API_URL`.
- FastAPI mantiene JWT, reglas de negocio, cálculos antropométricos, archivos y MySQL.
- Android continúa iniciando desde `main.py`; web inicia desde `web_main.py`.
- Las reglas de negocio son compartidas, pero los layouts Web y móvil son independientes cuando la densidad o el flujo lo requieren.

## Requisitos

- Python compatible con las dependencias del proyecto.
- MySQL configurado para FastAPI.
- `flet`, `flet-charts` y `flet-web` exactamente en versión `0.85.3`.
- Acceso HTTPS al backend para un despliegue público.

Instalación:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Variables de entorno

```text
API_URL=https://api.ejemplo.com/somatocarta
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8085
WEB_HOST=0.0.0.0
WEB_PORT=8550
WEB_ALLOWED_ORIGINS=https://somatocarta.ejemplo.com
SECRET_KEY=valor-largo-aleatorio
ACCESS_TOKEN_EXPIRE_MINUTES=30
DB_HOST=servidor-mysql
DB_PORT=3306
DB_USER=usuario
DB_PASSWORD=secreto
DB_NAME=somatocarta
```

`API_URL` no debe terminar en `/`. No se debe versionar `.env`. En producción no use `*` en `WEB_ALLOWED_ORIGINS`; declare únicamente los orígenes HTTPS autorizados separados por coma.

## Ejecución local

Terminal 1:

```powershell
.\start_backend.bat
```

Terminal 2:

```powershell
.\start_web.bat
```

Navegar a `http://localhost:8550`.

## Ejecución en servidor

Use la fábrica ASGI para evitar que el proceso intente abrir un navegador:

```bash
python -m uvicorn web_main:create_web_app --factory --host 127.0.0.1 --port 8550 --proxy-headers
```

Ejecute FastAPI en otro puerto o servicio:

```bash
python -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8085 --proxy-headers
```

Mantenga ambos procesos mediante systemd, Supervisor, Docker o el administrador de procesos del hosting.

## Proxy y HTTPS

El proxy inverso debe:

- Publicar Flet Web bajo un dominio o subdominio HTTPS.
- Mantener las cabeceras `Upgrade` y `Connection` para WebSocket.
- Enviar `X-Forwarded-Proto` y `X-Forwarded-For`.
- Publicar FastAPI bajo la URL indicada en `API_URL`.
- Permitir el tamaño requerido para fotografías y PDF.
- Definir tiempos de espera suficientes para conexiones WebSocket persistentes.

La aplicación no debe exponerse por HTTP cuando se utilicen credenciales reales.

## Fotografías y PDF

- El selector de archivos Flet envía la fotografía al proceso Flet y `ApiClient` la carga en `/files/upload` con su MIME.
- Las fotografías se visualizan desde la URL devuelta por FastAPI.
- Los PDF se solicitan con JWT desde el proceso Flet; en web se entregan al navegador, en escritorio se abren externamente y en Android se comparten mediante `ft.Share`.
- Los recursos visuales empaquetados usan nombres lógicos en Web y rutas locales en nativo mediante `asset_src`, conservando el mismo inventario visual.

## Comprobación

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_flet_web.py -q
.\.venv\Scripts\python.exe -m pytest -q
```

Antes de publicar, complete `docs/flet_web_qa_checklist.md` en los navegadores y tamaños objetivo.

El hosting no debe aplicar desafíos JavaScript de Imunify360 Bot Protection a la ruta de API. Excluya `/somatocarta/*` (o el subdominio API completo), porque los clientes Android/Python no pueden resolver un challenge de navegador.
