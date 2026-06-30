# Informe de pruebas integrales - Somatocarta v1.2.11

**Fecha:** 30 de junio de 2026  
**Rama:** `codex/add-flet-web`  
**APK:** `INSTALAR_Somatocarta_MOVIL_v1.2.11.apk`  
**Dispositivo:** Xiaomi `22101316UG`, Android 14, `arm64-v8a`

## 1. Dictamen

La version es **apta para pruebas internas controladas**, pero **no se recomienda su publicacion publica** hasta corregir los riesgos de autenticacion, firma y configuracion de seguridad descritos en este informe.

Resultado general: **aprobado con observaciones**.

| Area | Resultado |
|---|---|
| Suite automatizada | Aprobada |
| Integracion SQLite | Aprobada |
| API productiva de solo lectura | Aprobada |
| PDF individual y longitudinal | Aprobada |
| APK y arranque Android | Aprobado |
| Navegacion raiz y logout Android | Aprobados |
| Seguridad para produccion | No aprobada |
| Firma para distribucion publica | No aprobada |

## 2. Pruebas ejecutadas

### 2.1 Automatizacion

- `236` pruebas aprobadas.
- `7` subpruebas aprobadas.
- `0` fallos y `0` errores.
- Compilacion Python completa con `compileall`: aprobada.
- Preflight de publicacion: aprobado usando `ExecutionPolicy Bypass`.
- `pip check`: sin dependencias rotas.
- `pip-audit`: sin vulnerabilidades conocidas en `requirements.txt`.

La suite cubre autenticacion, validaciones, CRUD, integridad referencial, formulas antropometricas, PDF, API client, layouts, navegacion, busqueda movil y flujo E2E con base SQLite.

### 2.2 Cobertura

Cobertura global medida: **74%** (`5396` sentencias, `1390` sin ejecutar).

Coberturas destacadas:

| Modulo | Cobertura |
|---|---:|
| Modelos backend | 100% |
| Esquemas de deportistas | 98% |
| Dominio antropometrico | 96% |
| Componentes frontend | 91% |
| Navegacion | 90% |
| API client | 82% |
| Valoracion | 58% |
| Analisis longitudinal | 54% |
| Dashboard | 18% |
| Historial | 6% |

### 2.3 API desplegada

Pruebas realizadas contra `https://nyquist.app/somatocarta` con operaciones de solo lectura:

| Prueba | Estado | Tiempo aproximado |
|---|---:|---:|
| Health | 200 | 939 ms |
| Ruta protegida sin token | 401 | 754 ms |
| Login valido | 200 | 816 ms |
| Login invalido | 401 | - |
| Dashboard | 200 | 777 ms |
| Deportistas | 200 | 765 ms |
| Deportes | 200 | 733 ms |
| Entidades | 200 | 781 ms |
| Asignaciones | 200 | 739 ms |
| Historial | 200 | 845 ms |
| PDF individual | 200, `application/pdf` | 1767 ms |
| PDF longitudinal | 200, `application/pdf` | 1831 ms |

CORS permitio el origen configurado y rechazo un origen externo no autorizado.

### 2.4 APK y dispositivo real

- Paquete: `com.nyquist.somatocarta`.
- Version: `1.2.11`, `versionCode=22`.
- Android minimo: API 24.
- Android objetivo: API 36.
- ABIs: `arm64-v8a`, `armeabi-v7a`, `x86_64`.
- Firma APK v2 valida con certificado Android Debug.
- Instalacion por USB: aprobada.
- Arranque frio: `379 ms`.
- Proceso activo sin `FATAL EXCEPTION`, ANR ni `PlatformException`.
- Memoria observada: `157664 KB` PSS y `284448 KB` RSS.
- Login y Dashboard en dispositivo: aprobados.
- Atras desde Login: cierra la actividad sin pantalla blanca.
- Atras desde Dashboard: cierra la actividad sin pantalla blanca.
- Logout desde Dashboard: regresa a Login y elimina vistas protegidas.
- Compartir PDF: selector Android, URI temporal y MIME `application/pdf` verificados previamente en el mismo dispositivo.

La prueba manual Atras desde una pantalla secundaria no se completo durante esta corrida porque la pantalla solicitada no fue abierta. La pila secundaria si esta cubierta por pruebas automatizadas.

## 3. Aciertos

1. Suite estable sin fallos.
2. Integridad referencial y duplicados cubiertos por pruebas de base de datos.
3. Formulas antropometricas con pruebas de ramas y unidades.
4. API productiva disponible y con tiempos menores a dos segundos en la muestra.
5. Endpoints privados rechazan solicitudes sin token.
6. CORS restringe origenes no autorizados.
7. PDF individual y longitudinal validos y descargables.
8. Compartir PDF usa el servicio nativo Android.
9. Busquedas y CRUD moviles mantienen componentes compartidos.
10. Logout elimina la pila protegida.
11. El APK inicia rapidamente y no produjo crashes o ANR.
12. No se detectaron CVE conocidas ni dependencias rotas.

## 4. Inconsistencias

### Alta prioridad

#### SEG-01 - Contrasenas almacenadas/comparadas en texto plano

`src/backend/routers/auth.py` compara directamente `PSW_USER` con la contrasena recibida y `auth_utils.verify_password()` tambien permite comparacion plana.

**Riesgo:** exposicion total de credenciales ante acceso a la base de datos.  
**Accion:** migrar a bcrypt/Argon2, admitir transicion controlada y reemplazar el valor al siguiente login.

#### SEG-02 - Clave JWT insegura por defecto

`src/backend/auth_utils.py` usa `your-secret-key-keep-it-secret` cuando falta `SECRET_KEY`.

**Riesgo:** emision de tokens falsificados si produccion arranca sin variable segura.  
**Accion:** eliminar el valor por defecto y abortar el inicio si la variable no existe o es debil.

#### SEG-03 - Sin limitacion de intentos de login

No se encontro middleware o servicio de rate limiting.

**Riesgo:** fuerza bruta y abuso del endpoint.  
**Accion:** limitar por IP/usuario, introducir espera progresiva y alertas de auditoria.

### Prioridad media

#### QA-01 - Cobertura insuficiente en pantallas criticas

`historial.py` tiene 6%, Dashboard 18% y valoracion 58%.

**Accion:** agregar pruebas de interacciones reales, estados de error, paginacion, detalle, PDF y resize.

#### AND-01 - APK firmado con certificado debug

La firma v2 es valida, pero el firmante es `CN=Android Debug`.

**Accion:** crear keystore de release protegido y configurar firma reproducible para publicacion.

#### AND-02 - APK excesivamente grande

Tamano observado: `345907047` bytes, aproximadamente 330 MB.

**Accion:** publicar App Bundle o APK por ABI, revisar dependencias Python y excluir recursos no usados.

#### WEB-01 - Cabeceras HTTP defensivas ausentes

No se observaron `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy` ni `Referrer-Policy` en la ruta publica.

**Accion:** configurarlas en Apache/proxy; al menos HSTS y `nosniff` para la API.

#### TEC-01 - API Flet obsoleta

La suite emite `112` advertencias, principalmente por nueve usos de `ElevatedButton`, eliminado en Flet 1.0.

**Accion:** migrar a `ft.Button` antes de actualizar Flet.

### Prioridad baja / entorno

#### ENV-01 - Distribucion invalida en el entorno virtual

Pip advierte repetidamente `Ignoring invalid distribution -let-desktop`.

**Accion:** recrear el entorno virtual o retirar los metadatos corruptos.

#### ENV-02 - Preflight bloqueado por politica PowerShell

El script no inicia sin `-ExecutionPolicy Bypass` en este equipo.

**Accion:** documentar el comando compatible o firmar el script.

#### QA-02 - Automatizacion Android limitada por MIUI

MIUI rechazo `adb shell input` al no estar habilitada `Depuracion USB (ajustes de seguridad)`.

**Accion:** habilitarla en el dispositivo de QA o incorporar Appium/Android instrumentation en CI.

## 5. Criterio de salida

### Para pruebas internas

**Aprobado.** La aplicacion puede seguir usandose para validacion funcional controlada.

### Para produccion publica

**No aprobado.** Bloqueantes:

1. Migrar contrasenas a hash seguro.
2. Exigir una clave JWT fuerte.
3. Firmar con keystore de release.
4. Implementar proteccion contra fuerza bruta.

## 6. Orden recomendado

1. Resolver `SEG-01` y `SEG-02`.
2. Implementar `SEG-03`.
3. Configurar firma release.
4. Elevar cobertura de Historial y Dashboard.
5. Reducir tamano del APK.
6. Migrar controles Flet obsoletos.
7. Endurecer cabeceras HTTP y normalizar el entorno QA.
