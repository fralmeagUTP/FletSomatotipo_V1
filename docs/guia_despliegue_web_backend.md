# Guía paso a paso para montar Somatocarta Web y Backend

Esta guía describe cómo publicar Somatocarta con la arquitectura recomendada para un hosting sin VPS:

- **Backend FastAPI** en el hosting actual de `nyquist.app`.
- **Base de datos MySQL** en el hosting actual.
- **Frontend Flet Web** en Render.
- **Dominio público del frontend web**: `https://somatocarta.nyquist.app`.
- **URL pública del backend**: `https://nyquist.app/somatocarta`.

## 1. Arquitectura recomendada

```text
Usuario en navegador
        |
        v
https://somatocarta.nyquist.app
        |
        v
Render / Flet Web
        |
        v
https://nyquist.app/somatocarta
        |
        v
FastAPI Backend / Hosting
        |
        v
MySQL / Hosting
```

Esta separación es importante porque Flet Web necesita un proceso Python persistente y soporte WebSocket. En un hosting compartido sin VPS esto normalmente no es estable o no está soportado. Por eso el frontend web debe ir en Render u otra plataforma PaaS equivalente.

## 2. Requisitos previos

Antes de iniciar, verifica que tienes:

1. Acceso al panel del hosting de `nyquist.app`.
2. Acceso a la base de datos MySQL.
3. Acceso al repositorio GitHub del proyecto.
4. Cuenta en Render.
5. Acceso al DNS del dominio `nyquist.app`.
6. Backend funcionando localmente o en hosting.
7. Rama actualizada en GitHub con los archivos:
   - `web_main.py`
   - `render.yaml`
   - `requirements-web.txt`
   - `app_config.py`
   - `src/`
   - `views/`
   - `assets/`

## 3. Preparar el backend FastAPI

### 3.1 Archivos que deben estar en el hosting

En el hosting donde vive el backend, sube o actualiza estos archivos y carpetas:

```text
src/
views/
assets/
main.py
app_config.py
passenger_wsgi.py
requirements.txt
.env
```

No borres ni reemplaces esta carpeta si ya tiene fotos cargadas:

```text
src/backend/static/uploads/
```

Esa carpeta contiene fotografías de deportistas y otros archivos subidos por la aplicación.

### 3.2 Variables del backend

En el archivo `.env` del hosting configura las variables reales del backend.

Ejemplo:

```env
APP_ENV=production
API_URL=https://nyquist.app/somatocarta
WEB_ALLOWED_ORIGINS=https://somatocarta.nyquist.app

DB_HOST=tu_host_mysql
DB_PORT=3306
DB_NAME=tu_base_de_datos
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_password_mysql

SECRET_KEY=clave_segura_backend
JWT_SECRET_KEY=clave_segura_jwt
```

Notas:

- No subas el archivo `.env` real a GitHub.
- `WEB_ALLOWED_ORIGINS` permite que el frontend web en Render consuma el backend.
- Si pruebas localmente también puedes agregar orígenes locales separados por coma:

```env
WEB_ALLOWED_ORIGINS=https://somatocarta.nyquist.app,http://localhost:8550,http://127.0.0.1:8550
```

### 3.3 Instalar dependencias del backend

Desde el panel del hosting o terminal disponible, instala las dependencias:

```bash
pip install -r requirements.txt
```

Si el hosting usa entorno virtual, activa primero el entorno correspondiente.

### 3.4 Reiniciar backend

Si el hosting usa Passenger, reinicia la aplicación Python desde el panel.

También puedes forzar reinicio tocando el archivo de Passenger si tu hosting lo permite:

```bash
touch tmp/restart.txt
```

Si no existe la carpeta `tmp`, créala:

```bash
mkdir -p tmp
touch tmp/restart.txt
```

### 3.5 Verificar backend

Abre:

```text
https://nyquist.app/somatocarta/docs
```

Debe cargar la documentación Swagger de FastAPI.

También verifica:

```text
https://nyquist.app/somatocarta/openapi.json
```

Si Swagger no carga, revisa:

- Variables `.env`.
- Credenciales MySQL.
- Logs del hosting.
- Archivo `passenger_wsgi.py`.
- Instalación de dependencias.

## 4. Preparar el frontend Flet Web

### 4.1 Archivos usados por Render

Render usará principalmente estos archivos:

```text
render.yaml
requirements-web.txt
web_main.py
main.py
app_config.py
src/
views/
assets/
```

No necesitas subir manualmente el frontend a Render si Render está conectado a GitHub. Render leerá el repositorio directamente.

### 4.2 Contenido esperado de `render.yaml`

El proyecto debe tener un archivo `render.yaml` similar a este:

```yaml
services:
  - type: web
    name: somatocarta-web
    runtime: python
    buildCommand: python -m pip install -r requirements-web.txt
    startCommand: python -m uvicorn web_main:create_web_app --factory --host 0.0.0.0 --port $PORT --proxy-headers
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: APP_RUNTIME
        value: web
      - key: API_URL
        value: https://nyquist.app/somatocarta
```

### 4.3 Dependencias web

El archivo `requirements-web.txt` debe incluir las dependencias necesarias para Flet Web:

```text
flet==0.85.3
flet-charts==0.85.3
flet-web==0.85.3
python-dotenv
requests
uvicorn[standard]
pillow
```

## 5. Crear el servicio web en Render

### 5.1 Crear servicio desde Blueprint

En Render:

1. Entra a tu cuenta.
2. Selecciona `New`.
3. Selecciona `Blueprint`.
4. Conecta el repositorio GitHub del proyecto.
5. Selecciona la rama donde está la versión web.
6. Render detectará `render.yaml`.
7. Confirma la creación del servicio `somatocarta-web`.

### 5.2 Variables en Render

Verifica que el servicio tenga estas variables:

```env
APP_RUNTIME=web
API_URL=https://nyquist.app/somatocarta
PYTHON_VERSION=3.11.9
```

No agregues variables de MySQL en Render para el frontend web. El frontend no debe conectarse directamente a la base de datos.

### 5.3 Desplegar

Render ejecutará automáticamente:

```bash
python -m pip install -r requirements-web.txt
```

Luego iniciará la app con:

```bash
python -m uvicorn web_main:create_web_app --factory --host 0.0.0.0 --port $PORT --proxy-headers
```

Cuando el deploy termine, Render entregará una URL temporal parecida a:

```text
https://somatocarta-web.onrender.com
```

Abre esa URL y verifica que cargue el login.

## 6. Configurar el dominio `somatocarta.nyquist.app`

### 6.1 Agregar dominio en Render

En el servicio `somatocarta-web`:

1. Entra a `Settings`.
2. Busca `Custom Domains`.
3. Agrega:

```text
somatocarta.nyquist.app
```

4. Render mostrará un destino CNAME.

Ejemplo:

```text
somatocarta-web.onrender.com
```

El valor exacto debes copiarlo desde Render.

### 6.2 Crear CNAME en el DNS

En el panel DNS del dominio `nyquist.app`, crea un registro:

```text
Tipo: CNAME
Nombre: somatocarta
Destino: valor_entregado_por_render
TTL: automático o 3600
```

Ejemplo:

```text
Tipo: CNAME
Nombre: somatocarta
Destino: somatocarta-web.onrender.com
```

### 6.3 Esperar propagación

La propagación DNS puede tardar desde unos minutos hasta varias horas.

Puedes verificar con:

```bash
nslookup somatocarta.nyquist.app
```

Cuando el dominio responda, abre:

```text
https://somatocarta.nyquist.app
```

## 7. Validar CORS entre frontend y backend

Si el frontend carga pero no puede iniciar sesión o consultar datos, revisa CORS.

En el backend, `WEB_ALLOWED_ORIGINS` debe incluir:

```env
WEB_ALLOWED_ORIGINS=https://somatocarta.nyquist.app
```

Después de cambiar esta variable, reinicia el backend.

Síntomas típicos de CORS:

- El login no responde.
- En consola del navegador aparece error `CORS policy`.
- Las peticiones a `https://nyquist.app/somatocarta` son bloqueadas.

## 8. Pruebas funcionales obligatorias

Después del despliegue, prueba en navegador:

### 8.1 Login

1. Abre `https://somatocarta.nyquist.app`.
2. Ingresa usuario y contraseña.
3. Verifica que entre al dashboard.
4. Cierra sesión.
5. Verifica que vuelva al login.

### 8.2 Dashboard

Verifica:

- Carga visual correcta.
- Íconos visibles.
- Tarjetas con estilo correcto.
- Navegación a módulos.
- Diseño responsive en escritorio y móvil.

### 8.3 Deportistas

Verifica:

- Listado de deportistas.
- Crear deportista.
- Editar deportista.
- Eliminar deportista con confirmación.
- Cargar o cambiar fotografía.
- Visualizar fotografía guardada.

### 8.4 Entidades

Verifica:

- Listar entidades.
- Crear entidad.
- Editar entidad.
- Eliminar entidad con confirmación.

### 8.5 Deportes

Verifica:

- Listar deportes.
- Crear deporte.
- Editar deporte.
- Eliminar deporte con confirmación.

### 8.6 Asignaciones

Verifica:

- Crear asignaciones entre deportistas, entidades y deportes.
- Consultar asignaciones existentes.
- Eliminar asignaciones con confirmación.

### 8.7 Valoración corporal

Verifica:

- Buscar o seleccionar deportista.
- Registrar medición.
- Validar campos obligatorios.
- Guardar valoración.
- Confirmar que aparece en historial.

### 8.8 Historial y análisis individual

Verifica:

- Consultar historial de un deportista.
- Seleccionar valoración.
- Ver resultados.
- Ver somatocarta.
- Descargar PDF individual.

### 8.9 Análisis longitudinal

Verifica:

- Buscar deportista.
- Consultar evolución temporal.
- Ver gráficas.
- Descargar PDF longitudinal.

### 8.10 Fotos y archivos

Verifica:

- Carga de foto desde navegador.
- Persistencia después de recargar.
- Visualización en listado o formulario.
- Acceso a archivos subidos desde el backend.

## 9. Pruebas responsive

Prueba la web en estos tamaños:

```text
Escritorio: 1366 x 768
Tablet: 768 x 1024
Móvil: 390 x 844
```

Valida:

- Menú usable.
- Sin contenido cortado.
- Scroll vertical funcional.
- Botones visibles.
- Formularios editables.
- Tablas o listados legibles.
- Gráficas visibles.
- PDFs descargables.

## 10. Actualización de la aplicación

### 10.1 Actualizar frontend web

Cada vez que cambies el frontend web:

```bash
git add .
git commit -m "Describe el cambio"
git push
```

Render detectará el cambio y desplegará automáticamente.

Si no despliega automáticamente:

1. Entra al servicio en Render.
2. Selecciona `Manual Deploy`.
3. Selecciona `Deploy latest commit`.

### 10.2 Actualizar backend

Si cambias endpoints, lógica backend o modelos:

1. Sube al hosting los archivos modificados.
2. Instala dependencias nuevas si aplica.
3. Ejecuta migraciones o SQL si aplica.
4. Reinicia Passenger o la app Python.
5. Verifica `https://nyquist.app/somatocarta/docs`.

## 11. Checklist final de publicación

Antes de entregar la app web a usuarios, confirma:

- [ ] Backend abre en `https://nyquist.app/somatocarta/docs`.
- [ ] Frontend abre en `https://somatocarta.nyquist.app`.
- [ ] Login funciona.
- [ ] Token JWT se conserva durante la sesión.
- [ ] Cierre de sesión limpia el acceso.
- [ ] CORS permite el dominio web.
- [ ] Dashboard carga correctamente.
- [ ] Navegación funciona en escritorio.
- [ ] Navegación funciona en móvil.
- [ ] Deportistas funciona.
- [ ] Fotos funcionan.
- [ ] Entidades funciona.
- [ ] Deportes funciona.
- [ ] Asignaciones funciona.
- [ ] Valoración corporal funciona.
- [ ] Historial funciona.
- [ ] Análisis individual funciona.
- [ ] Análisis longitudinal funciona.
- [ ] PDF individual descarga.
- [ ] PDF longitudinal descarga.
- [ ] No hay secretos en GitHub.
- [ ] `.env` real solo existe en servidores.
- [ ] MySQL tiene integridad referencial aplicada.
- [ ] La carpeta de uploads no fue borrada.

## 12. Problemas comunes

### 12.1 El frontend carga pero no inicia sesión

Revisar:

- `API_URL` en Render.
- `WEB_ALLOWED_ORIGINS` en backend.
- Backend activo.
- Credenciales correctas.
- Consola del navegador.

### 12.2 Error CORS

Agregar al `.env` del backend:

```env
WEB_ALLOWED_ORIGINS=https://somatocarta.nyquist.app
```

Luego reiniciar backend.

### 12.3 Fotos no se ven

Revisar:

- Que `src/backend/static/uploads/` exista.
- Que no se haya borrado al subir archivos.
- Que el backend sirva archivos estáticos.
- Que las rutas de imágenes apunten al backend.

### 12.4 Render no despliega

Revisar:

- Logs de Render.
- `requirements-web.txt`.
- `web_main.py`.
- `render.yaml`.
- Versión de Python.

### 12.5 El dominio no abre

Revisar:

- CNAME en DNS.
- Dominio agregado en Render.
- Certificado SSL emitido por Render.
- Propagación DNS.

## 13. Comandos útiles

Ejecutar frontend web local:

```bash
python web_main.py
```

Ejecutar backend local:

```bash
python -m uvicorn src.backend.main:app --reload
```

Ejecutar pruebas:

```bash
pytest
```

Ver estado Git:

```bash
git status
```

Subir cambios:

```bash
git add .
git commit -m "Actualizar despliegue web"
git push
```

## 14. Decisión técnica final

### Diagnóstico de bloqueos por Imunify360

La ruta pública `/somatocarta` debe excluirse de **Bot Protection/Proactive Defense** en Imunify360. Un cliente Flet o Android no puede completar desafíos HTML y recibiría respuestas 415/503 aunque el navegador muestre correctamente el mensaje de estado de la API.

Verificar después del cambio que `POST /somatocarta/auth/login` acepte `application/json` desde una red externa. No se debe desactivar el firewall completo: la exclusión se limita a la ruta de la API.

Para un hosting sin VPS, la mejor opción es:

```text
Frontend Flet Web -> Render
Backend FastAPI   -> Hosting actual
Base de datos     -> MySQL del hosting
Dominio web       -> somatocarta.nyquist.app
API backend       -> nyquist.app/somatocarta
```

Esta arquitectura mantiene la app Android funcionando, permite publicar la versión web en navegador y evita depender de capacidades que normalmente no existen en hosting compartido.
