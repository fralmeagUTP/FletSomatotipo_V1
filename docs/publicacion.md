# Checklist de publicación

## Antes de hacer commit

1. Ejecutar pruebas:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

También puedes ejecutar el preflight local:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\preflight_publicacion.ps1
```

Para revisar archivos sin correr pruebas:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\preflight_publicacion.ps1 -SkipTests
```

2. Revisar estado:

```powershell
git status --short
```

3. Confirmar que no se publican secretos:

- `.env`
- credenciales de base de datos;
- tokens;
- logs locales.

4. Confirmar que no se publican artefactos generados:

- backups `Respaldo*.zip`;
- logs `*.log`;
- imágenes nuevas en `src/backend/static/uploads/`;
- carpetas `build/`, `dist/`, `.venv/`.

## Cambios que sí deberían incluirse

- `README.md`
- `docs/`
- `main.py`
- `app_config.py`
- `start_backend.bat`
- `start_frontend.bat`
- `start_web.bat`
- `web_main.py`
- `src/backend/`
- `src/frontend/`
- `views/`
- `tests/`
- `scripts/preflight_publicacion.ps1`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `passenger_wsgi.py` si se va a desplegar en cPanel/Passenger

## Publicación Flet Web

Antes de exponer la interfaz web:

- definir `API_URL` con HTTPS;
- definir `WEB_ALLOWED_ORIGINS` sin comodines;
- ejecutar Flet mediante `web_main:create_web_app --factory`;
- configurar el proxy inverso para conservar WebSocket;
- completar `docs/flet_web_qa_checklist.md` en escritorio, tablet y móvil;
- confirmar que fotografías y PDF funcionan desde el dominio final.

## Cambios que requieren decisión manual

- Imágenes históricas ya versionadas en `src/backend/static/uploads/`: decidir si deben permanecer en Git o migrarse fuera del repositorio.
- Backups o archivos de datos locales: mantenerlos fuera del repositorio.

## Uploads

La política operativa de archivos subidos está documentada en `docs/uploads.md`.

## Migraciones manuales de base de datos

Antes de desplegar cambios que dependen de restricciones nuevas en MySQL, ejecutar las migraciones pendientes contra la base de datos seleccionada.

```powershell
cmd /c "mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p %DB_NAME% < scripts\migrations\001_unique_somatotipo_deportista_fecha.sql"
```

La migración `001_unique_somatotipo_deportista_fecha.sql` crea el índice único `uq_somatotipo_deportista_fecha` sobre `CDRTablaSomatotipo(IDENTI_DEPORTISTA, FECHA_MEDIDA)`. Si existen duplicados previos, falla intencionalmente para obligar a depurar datos antes de activar la restricción.

Después, aplicar las restricciones de integridad referencial:

```powershell
cmd /c "mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p %DB_NAME% < scripts\migrations\002_referential_integrity.sql"
```

La migración `002_referential_integrity.sql` bloquea la eliminación o actualización de registros referenciados y evita deportes o asignaciones duplicadas. Se detiene sin cambiar el esquema si detecta datos huérfanos, incompletos o duplicados. La política completa está en `docs/integridad_referencial.md`.

En bases heredadas que ya tenían claves foráneas con reglas `CASCADE`, normalizar las reglas:

```powershell
cmd /c "mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p %DB_NAME% < scripts\migrations\003_normalize_foreign_keys_restrict.sql"
```

Esta migración conserva las relaciones, pero reemplaza `CASCADE` por `RESTRICT` tanto en actualización como en eliminación.

Para corregir y versionar las fórmulas antropométricas:

```powershell
cmd /c "mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p %DB_NAME% < scripts\migrations\004_correct_anthropometric_formulas.sql"
```

La migración `004` crea una copia de los detalles afectados antes de normalizar unidades y reemplazar las vistas de cálculo. Si detecta escalas mezcladas dentro de un registro, se detiene para exigir corrección manual.

En la base activa, las migraciones `002`, `003` y `004` están aplicadas. La verificación del 21 de junio de 2026 comparó 76 valoraciones y obtuvo 0 diferencias. Estos comandos siguen siendo obligatorios para nuevas bases, restauraciones o ambientes adicionales.

## Comando de commit sugerido

```powershell
git add .gitignore .env.example README.md docs main.py web_main.py app_config.py passenger_wsgi.py start_backend.bat start_frontend.bat start_web.bat requirements.txt scripts/preflight_publicacion.ps1 scripts/migrations src/backend src/frontend views tests
git commit -m "Mejora arquitectura frontend backend y pruebas"
```

Antes de ejecutar el commit, revisar que `git status --short` no incluya `.env`, backups nuevos ni uploads nuevos.
