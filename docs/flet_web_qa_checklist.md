# Checklist QA de Flet Web

## Instalación y seguridad

- [ ] `flet`, `flet-web` y `flet-charts` tienen versión `0.85.3`.
- [ ] `.env` no está versionado y no contiene credenciales de prueba públicas.
- [ ] `API_URL` apunta al backend correcto por HTTPS.
- [ ] `WEB_ALLOWED_ORIGINS` contiene solo dominios autorizados.
- [ ] El proxy conserva WebSocket y redirige HTTP a HTTPS.
- [ ] El JWT expira según `ACCESS_TOKEN_EXPIRE_MINUTES`.
- [ ] Cerrar sesión elimina el token y vuelve al login.

## Navegadores y responsive

- [x] Login y assets principales renderizados en Chrome a 390 × 844 px.
- [x] Todos los archivos versionados en `assets/` responden desde la aplicación ASGI.
- [ ] Chrome/Edge de escritorio a 1366 px o superior.
- [ ] Tablet horizontal y vertical entre 600 y 1199 px.
- [ ] Navegador móvil entre 320 y 599 px.
- [ ] El cambio de tamaño no cierra sesión ni pierde la pantalla activa.
- [ ] Escritorio muestra barra lateral y móvil muestra el botón de menú.
- [ ] El menú móvil abre, navega y cierra correctamente.
- [ ] No existe desplazamiento horizontal global que oculte acciones.
- [ ] Formularios, tablas, gráficos y diálogos permiten desplazamiento completo.

## Flujos funcionales

- [ ] Login válido abre Dashboard; login inválido muestra error.
- [ ] Dashboard carga métricas reales.
- [ ] Dashboard muestra iconos Material vectoriales uniformes y legibles.
- [ ] Deportistas permite listar, buscar, crear, editar y eliminar con confirmación.
- [ ] La fotografía se selecciona, previsualiza, guarda y vuelve a cargar.
- [ ] Entidades permite CRUD completo.
- [ ] Deportes permite CRUD completo.
- [ ] Asignaciones permite CRUD completo.
- [ ] Valoración corporal selecciona deportista, valida y guarda una medición.
- [ ] Historial muestra registros y análisis individual completo.
- [ ] Métodos de grasa, composición corporal, imágenes y somatocarta se muestran.
- [ ] El PDF individual se abre o descarga en el navegador.
- [ ] Análisis longitudinal muestra tendencias, trayectoria y somatocarta.
- [ ] El PDF longitudinal se abre o descarga en el navegador.
- [ ] Acerca del proyecto muestra textos y logotipos institucionales.

## Accesibilidad y errores

- [ ] Se puede recorrer login y acciones principales con teclado.
- [ ] El foco es visible y las etiquetas de campos son comprensibles.
- [ ] Texto y controles siguen legibles con zoom al 200%.
- [ ] Errores de red y validación producen mensajes visibles, no pantallas vacías.
- [ ] Una respuesta 401 limpia la sesión y solicita autenticación nuevamente.
- [ ] Fotografías o archivos inválidos son rechazados con un mensaje claro.

## Regresión Android

- [ ] `main.py` continúa iniciando la aplicación nativa.
- [ ] Login, navegación atrás, fotografías y PDF siguen funcionando en APK.
- [ ] No se añadieron dependencias web a `requirements-apk.txt`.
