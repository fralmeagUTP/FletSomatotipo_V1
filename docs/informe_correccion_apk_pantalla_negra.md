# Informe técnico — Corrección de pantalla negra en Android

**Proyecto:** Somatocarta v1.2.1  
**Fecha:** 21 de junio de 2026  
**Estado:** Corregido y verificado

## 1. Incidente

El APK anterior se instalaba correctamente, pero al abrirlo mostraba una pantalla vacía y no permitía utilizar la aplicación.

## 2. Diagnóstico

El problema fue reproducido en un emulador Android y se capturó el registro de ejecución mediante ADB. Python iniciaba, pero Flet no alcanzaba a ejecutar `main(page)` y generaba errores internos de conexión:

- `Broken pipe` en el socket interno de Flet.
- `Too many open files` después de múltiples intentos de conexión.
- El mismo comportamiento apareció en una aplicación Flet mínima, descartando inicialmente la lógica funcional de Somatocarta.

La causa principal fue el runtime Flet `0.28.3`, incompatible con el entorno Android generado actualmente.

## 3. Correcciones aplicadas

- Flet actualizado y fijado en la versión `0.85.3`.
- `flet-charts` agregado y fijado en `0.85.3`.
- Compatibilidad incorporada para APIs renombradas o separadas en Flet:
  - `ImageFit` / `BoxFit`.
  - Utilidades de `padding`, `margin`, `border` y `alignment`.
  - Controles de gráficos trasladados a `flet-charts`.
  - Compatibilidad del evento de selección de archivos.
- Eliminado el texto temporal de inicio antes de renderizar el formulario de acceso.
- Dependencias Python empaquetadas específicamente para ARM64.
- Incrementado `versionCode` de `2` a `3` para permitir actualizar la instalación anterior.

## 4. Validaciones realizadas

- Instalación mediante ADB: correcta.
- Inicio del proceso Python: correcto.
- Ejecución de `main(page)`: confirmada.
- Carga de módulos de la aplicación: correcta.
- Renderizado del formulario de inicio de sesión: correcto.
- Errores de arranque, `Traceback`, `Broken pipe` y `Too many open files`: ninguno en la validación final.
- Firma APK Scheme v2: verificada.
- Suite automatizada: `187 passed, 7 subtests passed`.

## 5. APK resultante

```text
build\apk\INSTALAR_Somatocarta_ARM64_v1.2.1.apk
```

- Paquete: `com.nyquist.somatocarta`
- Versión visible: `1.2.1`
- Código de versión: `7`
- Android mínimo: API 24, Android 7.0
- Arquitectura de dependencias Python: ARM64
- SHA-256: `C8D35A8558910087B74C86CFDA5AD20232DF445B9776D09881DEAA939E201309`
- Firma: debug, apta para pruebas internas, no para publicación en Google Play

## 6. Instrucciones de instalación

Instalar únicamente el siguiente archivo:

```text
INSTALAR_Somatocarta_ARM64_v1.2.1.apk
```

Puede instalarse sobre la versión anterior porque tiene un `versionCode` superior. Si Android informa que las firmas no coinciden, se debe desinstalar la versión anterior e instalar nuevamente; esta acción elimina los datos locales de esa instalación.

## 7. Resultado

La pantalla negra quedó corregida. La aplicación inicia, carga sus dependencias y presenta el formulario de acceso en Android.

## 8. Validación física

El APK final se instaló mediante ADB en un dispositivo Android 16 `arm64-v8a`. Se verificó el inicio de Python, la carga de módulos, el formulario de acceso y la navegación al Dashboard. La sesión se adaptó a `page.session.store`, API requerida por Flet 0.85.3.

## 9. Ajustes de navegación móvil

- Eliminada la búsqueda global del encabezado del Dashboard.
- Eliminada la búsqueda global superior de Valoración corporal, Historial corporal y Análisis longitudinal; cada pantalla conserva su búsqueda interna.
- Eliminada la búsqueda global superior de Deportistas, Deportes, Entidades y Asignaciones.
- Ajustados encabezados, anchos, scroll horizontal y expansión vertical para mostrar completos los análisis corporal y longitudinal en móvil.
- Migrados los gráficos longitudinales a la API de `flet-charts 0.85.3` (`points` y `label_size`), corrigiendo el fallo que impedía renderizar resultados en Android.
- El detalle del análisis corporal usa un `ListView` móvil y las imágenes de referencia se resuelven como assets lógicos, evitando cortes y rutas inválidas en Android.
- Eliminada la sección **Actividad reciente** del Dashboard.
- Sustituido el diálogo móvil incompatible por un panel desplegable integrado, desplazable y con cierre de sesión.
- Corregido el sufijo de unidades de Valoración corporal para evitar un `TypeError` en Android.
