# Política de uploads

**Fecha de actualización:** 22 de junio de 2026
**Estado:** validado por flujo E2E autenticado y pruebas del selector Android/Web.

## Alcance

Los archivos subidos por usuarios se guardan en `src/backend/static/uploads/` y se sirven desde `/static/uploads/`.

## Reglas actuales

- Solo se aceptan imágenes `jpg`, `jpeg` y `png`.
- El backend valida extensión, tipo MIME y tamaño máximo antes de guardar.
- Los nombres se generan con UUID para evitar colisiones y exposición del nombre local del archivo.
- Los uploads nuevos no deben versionarse en Git.
- El archivo `.gitkeep` conserva la carpeta vacía dentro del repositorio.
- El flujo E2E verifica carga PNG, almacenamiento temporal y asociación de la URL al deportista.
- Android y Web usan `FilePicker` como servicio y envían bytes junto con nombre y MIME explícito mediante `ApiClient.upload_photo()`.
- La previsualización usa bytes locales antes de guardar y la URL devuelta por FastAPI después de guardar.

## Operación local

Mantener la carpeta:

```powershell
src\backend\static\uploads
```

Si se clona el proyecto y no existe la carpeta, crearla antes de subir fotos o mantener `.gitkeep` versionado.

## Publicación

- En producción, revisar si conviene mover uploads fuera del repositorio o a almacenamiento externo.
- Hacer backup de la carpeta de uploads antes de migraciones o despliegues.
- No incluir imágenes personales de deportistas en commits, salvo decisión explícita.
- Revisar permisos de escritura del proceso backend sobre la carpeta de uploads.
- Si Web y FastAPI se publican en dominios distintos, permitir el origen web autorizado y servir las fotos por HTTPS.

## Riesgos a controlar

- Crecimiento de disco por imágenes acumuladas.
- Publicación accidental de fotos privadas en Git.
- Pérdida de archivos si la carpeta se borra durante despliegues.
- Desincronización entre base de datos y archivos si se eliminan fotos manualmente.
