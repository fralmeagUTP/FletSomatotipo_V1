# Guía rápida de inicio — Somatocarta v1.2.5

**Fusionado de:** `EJECUTAR_POWERSHELL.txt` + `comandos.txt`
**Fecha:** 29 de junio de 2026

---

## 1. Instalación

### Crear entorno virtual

```powershell
python -m venv .venv
```

### Instalar dependencias

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 2. Ejecución

### Opción rápida (scripts)

```powershell
# Terminal 1: Backend
.\start_backend.bat

# Terminal 2: Frontend (en otra terminal)
.\start_frontend.bat

# Alternativa Web
.\start_web.bat
```

### Opción manual (comandos directos)

```powershell
# Backend
.\.venv\Scripts\python.exe -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8085

# Frontend
.\.venv\Scripts\python.exe main.py

# Flet Web
.\.venv\Scripts\python.exe web_main.py
```

---

## 3. Configuración

La URL de la API se toma desde la variable `API_URL` en `.env`.

Si no existe, la aplicación usa el backend público `https://nyquist.app/somatocarta`. Para desarrollo local se recomienda definir explícitamente `API_URL=http://127.0.0.1:8085`.

Para Flet Web también se admiten:

```text
WEB_HOST=0.0.0.0
WEB_PORT=8550
WEB_ALLOWED_ORIGINS=http://localhost:8550,http://127.0.0.1:8550
```

### Acceder desde otro dispositivo en la red local

Agregar o cambiar en `.env`:

```text
API_URL=http://IP_DEL_PC:8085
```

Ejemplo:

```text
API_URL=http://192.168.1.106:8085
```

---

## 4. Verificación

| Endpoint | URL |
|----------|-----|
| API raíz | `http://127.0.0.1:8085/` |
| Documentación Swagger | `http://127.0.0.1:8085/docs` |
| Health check | `http://127.0.0.1:8085/health` |
| Flet Web | `http://127.0.0.1:8550/` |

---

## 5. Pruebas

### Ejecutar suite completa

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Estado esperado: **227 tests y 7 subpruebas pasando**.

### Ejecutar con resumen

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

---

## 6. Build APK (Android)

```powershell
.\.venv\Scripts\flet.exe build apk . --project somatocarta --product Somatocarta --org com.nyquist --bundle-id com.nyquist.somatocarta --build-version 1.2.5 --build-number 12
```

El archivo queda en: `build\apk\Somatocarta.apk`

El APK no incluye `.env`; por defecto usa `https://nyquist.app/somatocarta`. En escritorio, `API_URL` definido en `.env` sigue teniendo prioridad.

### APK de pruebas móviles

El build optimizado usa `requirements-apk.txt` para evitar empaquetar dependencias exclusivas del backend. Artefacto verificado:

```text
build\apk\INSTALAR_Somatocarta_MOVIL_v1.2.5.apk
```

- Paquete: `com.nyquist.somatocarta`
- Versión: `1.2.5` (`versionCode=12`)
- Android mínimo: API 24 (Android 7.0)
- Arquitecturas: `arm64-v8a`, `armeabi-v7a` y `x86_64`
- Runtime: Flet `0.85.3` y `flet-charts 0.85.3`
- Firma: debug, válida únicamente para instalación y pruebas internas

Instalación mediante USB con depuración habilitada:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r .\build\apk\INSTALAR_Somatocarta_MOVIL_v1.2.5.apk
```

La estructura, firma, manifiesto, versión y arquitecturas del APK fueron verificadas con Android Build Tools 35.0.0.

SHA-256: `68AFB85A48A6475653F3A0D55A90F97936BF283953A2BD597538DBE7A4E38B8F`.

La entrega móvil permite compartir PDF individuales y longitudinales con aplicaciones instaladas mediante `ACTION_SEND` y el `FileProvider` del paquete.

Para publicación se debe generar y proteger un keystore de release propio; no distribuir públicamente el APK firmado con certificado debug.

---

## 7. Sincronización con repositorio

```powershell
git pull origin main
git push origin main --tags
```

---

## 8. Documentación adicional

| Recurso | Ubicación |
|---------|-----------|
| Resumen del proyecto | `README.md` |
| Arquitectura técnica | `docs/architecture.md` |
| Módulos funcionales | `docs/modules.md` |
| Especificación completa | `docs/specs/somatocarta_spec.md` |
| Guía de usuario | `docs/user_guide.md` |
| Fórmulas y cálculos | `docs/formulas_somatotipo.md` |
| Integridad referencial | `docs/integridad_referencial.md` |
| Estado funcional vigente | `docs/estado_funcional.md` |
| Plan de pruebas | `docs/testing_plan.md` |
| Gobernanza y changelog | `docs/documentation_governance.md`, `docs/changelog_documentation.md` |
| Despliegue Flet Web | `docs/flet_web_deployment.md` |
| QA Flet Web | `docs/flet_web_qa_checklist.md` |
