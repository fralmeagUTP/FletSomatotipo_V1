# Guía de usuario — Somatocarta v1.1.7

**Fecha:** 15 de junio de 2026

---

## 1. Introducción

Somatocarta es una aplicación para registrar deportistas, realizar valoraciones antropométricas, analizar la composición corporal y el somatotipo, y generar informes PDF. Forma parte del sistema SINVADE (Sistema Integral de Valoración Deportiva).

### 1.1 Requisitos

- Python 3.10+ instalado.
- Entorno virtual configurado (`.venv`).
- Backend FastAPI corriendo en `http://127.0.0.1:8085`.
- Base de datos MySQL accesible.

### 1.2 Inicio rápido

```powershell
# Terminal 1: Backend
.\start_backend.bat

# Terminal 2: Frontend
.\start_frontend.bat
```

---

## 2. Inicio de sesión

1. Al abrir la aplicación, verá la pantalla de inicio de sesión con el logotipo de Somatocarta.
2. Ingrese su **usuario** y **contraseña**.
3. Pulse **Iniciar sesión**.
4. Si las credenciales son correctas, accederá al Dashboard.
5. Si son incorrectas, verá un mensaje de error en rojo.

> **Nota:** Si olvida sus credenciales, contacte al administrador del sistema.

---

## 3. Dashboard

El Dashboard es la pantalla principal. Muestra:

- **Saludo personalizado** con su nombre de usuario.
- **Tarjetas de métricas:** total de deportistas, valoraciones, asignaciones y estado del sistema.
- **Actividad reciente:** últimas valoraciones registradas.
- **Módulos del sistema:** accesos rápidos a cada funcionalidad.
- **Botón de cerrar sesión** en la esquina superior derecha.

### Navegación

- **Escritorio:** Use el menú lateral izquierdo para navegar entre módulos.
- **Móvil/Tablet:** Use el botón de menú (☰) para acceder a los módulos.
- **Búsqueda global:** Escriba el nombre de un deportista en la barra de búsqueda para acceder rápidamente a su valoración o historial.

---

## 4. Gestión de Deportistas

### 4.1 Listar deportistas

1. Desde el menú, seleccione **Deportistas**.
2. Verá una tabla con todos los deportistas registrados.
3. Use la barra de búsqueda para filtrar por nombre o identificación.
4. Use los botones de paginación para navegar entre páginas.

### 4.2 Crear un deportista

1. Pulse el botón **Nuevo deportista**.
2. Complete el formulario en 3 pestañas:
   - **Datos básicos:** Identificación, tipo de documento, nombre, sexo, fecha de nacimiento.
   - **Ubicación y contacto:** País, departamento, ciudad, dirección, teléfono, email.
   - **Socio-económico:** Estrato, nivel educativo, institución, observaciones.
3. Opcionalmente, cargue una fotografía (JPG o PNG, máximo 5 MB).
4. Pulse **Guardar**.

> **Campos obligatorios:** Identificación, tipo de documento, nombre y sexo.

### 4.3 Editar un deportista

1. En la lista, pulse el ícono de editar (✏️) junto al deportista.
2. Modifique los campos necesarios.
3. Pulse **Actualizar**.

### 4.4 Eliminar un deportista

1. En la lista, pulse el ícono de eliminar (🗑️).
2. Confirme la eliminación en el diálogo.

> **Advertencia:** Si el deportista tiene valoraciones asociadas, estas también se eliminarán.

---

## 5. Gestión de Entidades

### 5.1 Listar entidades

1. Desde el menú, seleccione **Entidades**.
2. Verá las entidades registradas (ligas, clubes, instituciones).

### 5.2 Crear una entidad

1. Pulse **Nueva entidad**.
2. Complete: NIT, razón social, teléfono, contacto, email.
3. Pulse **Guardar**.

### 5.3 Editar / Eliminar

Use los íconos de editar o eliminar junto a cada entidad.

---

## 6. Gestión de Deportes

### 6.1 Listar deportes

1. Desde el menú, seleccione **Deportes**.

### 6.2 Crear un deporte

1. Pulse **Nuevo deporte**.
2. Escriba el nombre del deporte.
3. Pulse **Guardar**.

---

## 7. Asignaciones

Las asignaciones relacionan un deportista con una entidad y un deporte.

### 7.1 Crear una asignación

1. Desde el menú, seleccione **Asignaciones**.
2. Busque el deportista.
3. Seleccione el deporte y la entidad en los dropdowns.
4. Pulse **Guardar**.

### 7.2 Editar / Eliminar

Use los íconos correspondientes en la lista de asignaciones.

---

## 8. Valoración Corporal

### 8.1 Iniciar una valoración

1. Desde el menú, seleccione **Valoración Corporal**.
2. Busque el deportista por nombre o identificación.
3. Aparecerá una tarjeta con los datos del deportista.

### 8.2 Capturar mediciones

El formulario tiene 14 campos organizados en grupos:

**Datos básicos:**
- Estatura (cm)
- Peso (kg)

**Pliegues cutáneos (mm):**
- Tricipital
- Subescapular
- Suprailiaco
- Abdominal
- Muslo anterior
- Pierna medial

**Diámetros (mm):**
- Muñeca
- Fémur
- Codo

**Perímetros (mm):**
- Bíceps contraído
- Pierna
- Circunferencia de carpo

### 8.3 Agregar tomas de medición

Puede registrar múltiples tomas (repeticiones) para cada valoración:

1. Complete los 14 campos.
2. Pulse **Agregar medición**.
3. La toma se agrega a la lista de revisiones.
4. Puede agregar más tomas, editarlas o eliminarlas antes de guardar.

### 8.4 Guardar la valoración

1. Revise las tomas agregadas.
2. Seleccione la fecha de medición.
3. Opcionalmente, agregue observaciones.
4. Pulse **Guardar valoración**.

> **Nota:** No se permite registrar dos valoraciones del mismo deportista en la misma fecha.

### 8.5 Cargar una valoración almacenada

1. En la sección de valoraciones almacenadas, busque la valoración deseada.
2. Pulse **Cargar**.
3. Podrá editar las mediciones existentes o agregar nuevas tomas.

---

## 9. Análisis de Valoración (Historial)

### 9.1 Consultar historial

1. Desde el menú, seleccione **Historial**.
2. Busque el deportista.
3. Verá una lista de todas sus valoraciones.

### 9.2 Ver detalle de una valoración

Seleccione una valoración para ver:

- **Medidas:** Los 14 campos antropométricos.
- **Composición corporal:**
  - Comparación de 3 métodos de grasa (Johnston, Faulkner, Yuhasz).
  - Distribución de masas (grasa, muscular, ósea, residual).
  - Gráfico de pastel.
- **IMC:** Valor y clasificación con imagen de referencia.
- **Complexión física:** Valor y tipo con imagen de referencia.
- **Somatotipo:** Endomorfismo, mesomorfismo, ectomorfismo con escalas descriptivas.
- **Somatocarta:** Carta de Heath-Carter con ubicación del deportista.

### 9.3 Descargar PDF individual

1. En el detalle de la valoración, pulse **Descargar PDF**.
2. El archivo se guardará en su carpeta de descargas.

### 9.4 Eliminar una valoración

1. En el detalle, pulse **Eliminar valoración**.
2. Confirme la acción.

---

## 10. Análisis Longitudinal

### 10.1 Acceder al análisis

1. Desde el menú, seleccione **Análisis Longitudinal**.
2. Busque el deportista.
3. El sistema debe tener al menos 2 valoraciones para mostrar el análisis.

### 10.2 Contenido del análisis

- **Tarjetas KPI:** Valor inicial, valor final, cambio absoluto y porcentaje de cambio.
- **Gráficos de línea:** Evolución temporal de 11 variables.
- **Comparación de métodos de grasa:** Johnston vs Faulkner vs Yuhasz.
- **Somatocarta longitudinal:** Todos los puntos X, Y con trayectoria cronológica.
- **Peso vs masa muscular:** Gráfico comparativo.
- **Tabla histórica:** Todas las valoraciones con sus valores.

### 10.3 Descargar PDF longitudinal

Pulse **Descargar PDF longitudinal** para obtener el informe completo.

---

## 11. Acerca del Proyecto

Desde el menú, seleccione **Acerca del Proyecto** para ver:

- Descripción del proyecto Somatocarta.
- Alcance y funcionalidades.
- Logotipos institucionales de las entidades vinculadas.

---

## 12. Cerrar sesión

1. Pulse el botón **Cerrar sesión** en la esquina superior derecha del Dashboard.
2. O pulse el ícono de salir (🚪) en el menú lateral.
3. Será redirigido a la pantalla de inicio de sesión.

---

## 13. Solución de problemas

| Problema | Posible causa | Solución |
|----------|---------------|----------|
| "No se pudo conectar con el servidor" | Backend no está corriendo | Ejecute `start_backend.bat` |
| "Credenciales incorrectas" | Usuario o contraseña erróneos | Verifique sus credenciales |
| "Sesión expirada" | Token JWT vencido | Inicie sesión nuevamente |
| PDF no se descarga | Problema de red o permisos | Verifique conexión y carpeta de descargas |
| Pantalla en blanco | Error de carga | Cierre y reabra la aplicación |

---

## 14. Soporte

Para reportar problemas o solicitar asistencia, contacte al equipo de desarrollo del proyecto Somatocarta.
