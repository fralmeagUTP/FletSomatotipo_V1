# Guía rápida de inicio — Somatocarta v1.1.7

**Fusionado de:** `EJECUTAR_POWERSHELL.txt` + `comandos.txt`
**Fecha:** 15 de junio de 2026

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
```

### Opción manual (comandos directos)

```powershell
# Backend
.\.venv\Scripts\python.exe -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8085

# Frontend
.\.venv\Scripts\python.exe main.py
```

---

## 3. Configuración

La URL de la API se toma desde la variable `API_URL` en `.env`.

Si no existe, se usa por defecto: `http://127.0.0.1:8085`

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

---

## 5. Pruebas

### Ejecutar suite completa

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Estado esperado: **162 tests pasando**.

### Ejecutar con resumen

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

---

## 6. Build APK (Android)

```powershell
.\.venv\Scripts\flet.exe build apk
```

El archivo queda en: `build\apk\app-release.apk`

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
| Plan de pruebas | `docs/testing_plan.md` |
