# Arquitectura de Somatocarta

## Objetivo

Somatocarta es una aplicación Flet + FastAPI para gestionar deportistas, registrar valoraciones antropométricas y consultar historial de somatotipo.

## Estructura principal

```text
main.py                         # Entrada del frontend Flet
app_config.py                   # Configuración compartida del frontend
views/                          # Pantallas Flet
src/frontend/                   # Cliente API, navegación, tema y helpers UI
src/backend/main.py             # Entrada FastAPI
src/backend/routers/            # Capa HTTP/API
src/backend/schemas/            # Modelos Pydantic de entrada/salida
src/backend/services/           # Reglas de aplicación y transacciones DB
src/backend/models.py           # Modelos SQLAlchemy
tests/                          # Pruebas automatizadas
```

## Flujo frontend

1. `main.py` muestra login.
2. `ApiClient.login()` autentica contra `/auth/login`.
3. La sesión guarda `access_token`, `username`, `login_user` y `user_id`.
4. Las vistas usan `ApiClient` para consumir backend.
5. `src/frontend/navigation.py` centraliza cambios de pantalla.
6. `src/frontend/components.py`, `theme.py`, `form_helpers.py` y `table_builders.py` reducen duplicación visual y lógica.

## Flujo backend

1. `src/backend/main.py` registra routers.
2. Los routers validan request/response con schemas Pydantic.
3. Los routers delegan operaciones a servicios.
4. Los servicios usan modelos SQLAlchemy y controlan `commit()` / `rollback()`.
5. Las rutas privadas usan `Depends(get_current_user)`.

## Endpoints principales

- `POST /auth/login`: autenticación.
- `GET /deportistas/`: listado paginado de deportistas.
- `POST /deportistas/`: creación de deportista.
- `PUT /deportistas/{identi}`: actualización.
- `DELETE /deportistas/{identi}`: eliminación.
- `POST /somatotipo/`: registro de valoración.
- `GET /somatotipo/vista/deportista/{identi}`: historial paginado.
- `POST /files/upload`: carga de imagen validada.

## Paginación

Los listados devuelven:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 10
}
```

El cliente mantiene métodos compatibles que devuelven solo `items` cuando la vista no necesita metadata.

## Pruebas

La suite cubre:

- seguridad básica de API;
- validación de schemas;
- servicios backend y rollback;
- cliente API frontend;
- helpers de formularios;
- componentes UI;
- builders de tablas/listas.

Comando:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

## Decisiones relevantes

- La URL del backend se centraliza en `app_config.py`.
- Las rutas privadas están protegidas por token.
- El frontend no debe usar `requests` directamente fuera de `ApiClient`.
- Los routers no deben contener lógica de transacción; esa responsabilidad está en servicios.
- Los schemas Pydantic viven fuera de routers para mantener separación de capas.

## Pendientes recomendados

- Añadir base de datos de test controlada para pruebas de integración reales.
- Documentar fórmulas clínicas/cálculos de somatotipo si se editan.
- Añadir migraciones de base de datos si el modelo empieza a cambiar.
- Limpiar binarios/backups e imágenes generadas antes de publicar cambios.
