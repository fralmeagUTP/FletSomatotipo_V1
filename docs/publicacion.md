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
- `src/backend/`
- `src/frontend/`
- `views/`
- `tests/`
- `scripts/preflight_publicacion.ps1`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `passenger_wsgi.py` si se va a desplegar en cPanel/Passenger
- `EJECUTAR_POWERSHELL.txt`
- `comandos.txt`

## Cambios que requieren decisión manual

- `Respaldo_v1.1.1.zip`: aparece modificado y ya está versionado. No conviene incluirlo salvo que sea intencional.
- Imágenes históricas ya versionadas en `src/backend/static/uploads/`: decidir si deben permanecer en Git o migrarse fuera del repositorio.

## Uploads

La política operativa de archivos subidos está documentada en `docs/uploads.md`.

## Migraciones manuales de base de datos

Antes de desplegar cambios que dependen de restricciones nuevas en MySQL, ejecutar las migraciones pendientes contra la base de datos seleccionada.

```powershell
mysql -h $env:DB_HOST -P $env:DB_PORT -u $env:DB_USER -p $env:DB_NAME < .\scripts\migrations\001_unique_somatotipo_deportista_fecha.sql
```

La migración `001_unique_somatotipo_deportista_fecha.sql` crea el índice único `uq_somatotipo_deportista_fecha` sobre `CDRTablaSomatotipo(IDENTI_DEPORTISTA, FECHA_MEDIDA)`. Si existen duplicados previos, falla intencionalmente para obligar a depurar datos antes de activar la restricción.

## Comando de commit sugerido

```powershell
git add .gitignore .env.example README.md docs main.py app_config.py passenger_wsgi.py start_backend.bat start_frontend.bat requirements.txt EJECUTAR_POWERSHELL.txt comandos.txt scripts/preflight_publicacion.ps1 src/backend src/frontend views tests
git commit -m "Mejora arquitectura frontend backend y pruebas"
```

Antes de ejecutar el commit, revisar que `git status --short` no incluya `.env`, backups nuevos ni uploads nuevos.
