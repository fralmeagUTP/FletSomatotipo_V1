# Changelog documental

## 29 de junio de 2026 — Release v1.2.5

- Separadas las composiciones visuales Web y Android sin duplicar reglas de negocio.
- Rediseñado CRUD móvil de deportistas (cuatro pasos), deportes, entidades y asignaciones.
- Corregidos nombres y datos completos del deportista en asignaciones.
- Restaurado todo el contenido longitudinal en móvil con secciones adaptadas.
- Habilitados mostrar/ocultar contraseña y cierre de sesión desde el encabezado móvil.
- Normalizado el orden de logotipos: UTP, ISC, Programa de Deportes y Nyquist.
- Añadido compartir PDF individual y longitudinal mediante selector Android, `ACTION_SEND` y `FileProvider`.
- Mejorado login backend con respuesta 503 controlada ante indisponibilidad SQL.
- Documentada la incompatibilidad de Imunify360 Bot Protection con clientes API nativos.
- APK generado: `INSTALAR_Somatocarta_MOVIL_v1.2.5.apk`, `versionCode=12`, API 24+, arquitecturas `arm64-v8a`, `armeabi-v7a` y `x86_64`.
- Firma de pruebas Android v2 verificada y SHA-256 `68AFB85A48A6475653F3A0D55A90F97936BF283953A2BD597538DBE7A4E38B8F`.
- Suite final: 227 pruebas y 7 subpruebas aprobadas.

Este archivo registra cambios que afectan el estado, alcance o interpretación de la documentación de Somatocarta.

## 22 de junio de 2026 — Primera versión Flet Web

- Añadida especificación Spec Kit en `docs/specs/flet_web/`.
- Añadidos `web_main.py` y `start_web.bat` reutilizando la entrada, vistas, tema, activos y `ApiClient` existentes.
- Añadida fábrica ASGI para despliegue web sin interfaz gráfica.
- Fijada la dependencia `flet-web==0.85.3` para mantener compatibilidad con Flet.
- Añadida configuración de host, puerto y orígenes CORS mediante variables de entorno.
- Adaptadas las descargas PDF para navegador sin cambiar el guardado nativo de Android/escritorio.
- Añadidas guía de despliegue, checklist QA web y pruebas automatizadas de arranque HTTP.
- Corregidas las rutas absolutas de Login, Dashboard y Acerca para servir en Web los mismos assets de Android.
- Verificados todos los recursos de `assets/` desde ASGI y el login responsive real en Chrome a 390 × 844 px.
- Sustituidas las miniaturas PNG del Dashboard por iconos Material vectoriales uniformes, legibles en Web y Android.
- Sincronizados README, arquitectura, módulos, guía de usuario, quickstart, publicación, uploads, planes y checklists con el estado funcional del 95% y 206 pruebas aprobadas.
- Añadida configuración sin VPS mediante Render, dependencias Web separadas y dominio recomendado `somatocarta.nyquist.app`, conservando FastAPI/MySQL en cPanel.

## 22 de junio de 2026 — Release v1.2.1

- Integridad referencial reforzada mediante migraciones SQL y respuestas HTTP 409 para dependencias activas.
- Fórmulas antropométricas centralizadas, corregidas y verificadas contra los datos históricos.
- Confirmaciones de eliminación incorporadas en los módulos CRUD.
- Dashboard y navegación móvil simplificados y adaptados a Android.
- Análisis corporal, longitudinal, gráficos y generación de PDF ajustados para pantallas móviles.
- Pantalla Deportistas migrada a controles compatibles con Android; `FilePicker` se registra como servicio y permite cargar o cambiar fotografías desde almacenamiento o galería.
- Retroceso Android configurado mediante navegación de rutas y callback clásico del manifiesto.
- APK ARM64 `versionCode=8`, versión visible `1.2.1` y firma verificada; SHA-256 `C8D35A8558910087B74C86CFDA5AD20232DF445B9776D09881DEAA939E201309`.
- Suite automatizada completa aprobada.

## 21 de junio de 2026 — Navegación móvil

- Dashboard simplificado sin buscador global ni actividad reciente.
- Menú móvil convertido en panel desplegable con navegación completa y cierre de sesión.
- Corregida la apertura de Valoración corporal en Android.
- Eliminado el buscador global superior de Valoración corporal, Historial corporal y Análisis longitudinal.
- Eliminado el buscador global superior de Deportistas, Deportes, Entidades y Asignaciones.
- Mejorado el layout móvil de Historial corporal y Análisis longitudinal con contenido expandible y desplazamiento completo.
- Corregido el renderizado de gráficos longitudinales para la API de `flet-charts 0.85.3` usada por Android.
- Corregidos el scroll del detalle corporal y la carga de imágenes de referencia empaquetadas en Android.
- Corregida la seccion Metodos de grasa en Historial corporal: se reemplazo la tabla por tarjetas responsivas y el grafico de masas usa `flet-charts`.
- Eliminados `FilePicker`, `Tabs` y `TabBar` de Deportistas por incompatibilidad con el runtime visual distribuido.
- El formulario de Deportistas ahora usa una única vista responsive y desplazable, compatible con escritorio y móvil.
- Añadida una prueba que construye completamente la vista y confirma que no se agregan controles incompatibles.
- Corregida la apertura de los diálogos Agregar, Editar y Eliminar mediante controles `overlay` compatibles.
- La columna Acciones ahora aparece primero para mantenerse visible en escritorio y móvil.
- Añadidas pruebas que ejecutan los tres botones y confirman la eliminación contra la API simulada.
- Añadido historial de rutas para que el botón Atrás del sistema Android restaure la pantalla anterior.
- Todas las pantallas principales registran rutas independientes sin cerrar la sesión activa.
- Añadida prueba Dashboard → Deportistas → Atrás → Dashboard.
- Corregida la navegación posterior al login: `Page.push_route` ahora se ejecuta como corrutina mediante `page.run_task`.
- La pantalla solicitada se renderiza antes de registrar la ruta, evitando que el login quede detenido.
- Añadida prueba con `push_route` asíncrono y validación sin `RuntimeWarning`.
- APK ARM64 actualizado con SHA-256 `135744DE15238742C364D829441CD6ECC3EFB860A943EF2F0CD338FB6216B760`.
- Suite verificada: `187 passed, 7 subtests passed`.

## 21 de junio de 2026

### Estado funcional

- Estado ponderado actualizado a 94%.
- Suite verificada: 183 pruebas y 3 subpruebas aprobadas.
- Base MySQL activa: 76 valoraciones verificadas, 0 diferencias de fórmula.
- Backend verificado mediante `GET /health` con base de datos conectada.

### Cambios funcionales documentados

- Migraciones `002` y `003`: claves foráneas, restricciones únicas y política `RESTRICT` activas.
- Migración `004`: unidades históricas y fórmulas antropométricas corregidas.
- Eliminaciones: confirmación visual y bloqueo de dependencias mediante HTTP 409.
- Responsive: shell dinámico entre sidebar y menú móvil.
- E2E: login, fotografía, CRUD, asignación, valoración, edición, PDFs y limpieza.
- PDFs: contenido variable por deportista y optimización de imágenes con Pillow.
- Sesión: expiración JWT unificada y configurable, con 30 minutos por defecto.
- Cierre de sesión: una respuesta 401 limpia todas las variables locales de sesión.
- APK: fallback de `API_URL` confirmado contra el backend público porque `.env` se excluye del paquete móvil.
- APK corregido `INSTALAR_ESTE_Somatocarta_v1.1.7.apk` regenerado con `versionCode=3`, ARM64, API 24+, Flet 0.85.3 y firma debug verificada.
- Android: corregida la pantalla negra causada por Flet 0.28.3; el login fue validado en emulador sin excepciones de arranque.
- Android: APK ARM64 puro con `versionCode=7`, recursos compatibles con Android 16, servicios de corrutinas preservados y sesión migrada a `page.session.store`; login y Dashboard verificados en dispositivo físico.
- Dashboard: el buscador global cierra el diálogo antes de navegar y carga automáticamente el deportista en Valoración o Historial.

### Documentos actualizados

- `README.md`
- `docs/architecture.md`
- `docs/documentation_governance.md`
- `docs/estado_funcional.md`
- `docs/formulas_somatotipo.md`
- `docs/integridad_referencial.md`
- `docs/modules.md`
- `docs/publicacion.md`
- `docs/qa_checklist.md`
- `docs/quickstart.md`
- `docs/testing_plan.md`
- `docs/uploads.md`
- `docs/user_guide.md`
- `docs/specs/somatocarta_spec.md`

### Informes históricos

Los archivos de `docs/qa/` conservan resultados de sesiones anteriores. Se etiquetaron como históricos y no deben utilizarse para determinar el estado actual del proyecto.

## 15 de junio de 2026

- Consolidación inicial de documentos redundantes.
- Organización de especificaciones en `docs/specs/` e informes en `docs/qa/`.
- Creación de la arquitectura, guía rápida y gobernanza documental iniciales.
