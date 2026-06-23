# Especificación: Somatocarta Flet Web

## Objetivo

Construir una primera versión web de Somatocarta ejecutada con Flet Web y accesible desde navegadores modernos, reutilizando el frontend Flet existente y el backend FastAPI actual. La incorporación no debe alterar el comportamiento de la aplicación Android.

## Funcionalidad incluida

- Inicio y cierre de sesión mediante JWT.
- Dashboard operativo.
- Gestión de deportistas, incluida la carga y visualización de fotografías.
- Gestión de entidades, deportes y asignaciones.
- Registro de valoración corporal.
- Historial y análisis individual de valoraciones.
- Análisis longitudinal.
- Visualización de somatocarta.
- Solicitud y descarga de informes PDF individuales y longitudinales.
- Página Acerca de.
- Navegación responsive entre todos los módulos disponibles.

Los cálculos antropométricos y clínicos seguirán ejecutándose exclusivamente en FastAPI y sus servicios de dominio.

## Módulos conservados

La versión web conservará los nombres y flujos actuales: Dashboard, Valoración corporal, Deportistas, Análisis de valoración corporal, Análisis longitudinal, Deportes, Entidades, Asignaciones y Acerca del proyecto.

## Identidad visual

Se mantendrán los recursos y componentes actuales:

- Paleta azul institucional, fondos claros y colores semánticos definidos en `src/frontend/theme.py`.
- Logotipo de Somatocarta y logotipos institucionales existentes en `assets/`.
- Tarjetas blancas, bordes suaves, radios, espaciado y jerarquía tipográfica actuales.
- Iconografía Material de Flet.
- Barra lateral en escritorio y menú compacto en pantallas estrechas.
- Textos, etiquetas, títulos y orden de módulos de la aplicación Android.

No se realizará un rediseño visual independiente para web.

## Usuarios

- Administradores y operadores autorizados que registran deportistas y valoraciones.
- Profesionales que consultan análisis individuales y longitudinales.
- Personal institucional que opera desde escritorio, tablet o navegador móvil.

## Requisitos responsive

- **Escritorio (>= 1200 px):** barra lateral persistente, contenido expandido y tablas completas cuando exista espacio.
- **Tablet (600-1199 px):** menú compacto, tarjetas y formularios reorganizados sin desplazamiento horizontal global.
- **Móvil (< 600 px):** navegación mediante menú, controles táctiles, columnas apiladas y desplazamiento vertical completo.
- Ninguna vista debe depender de dimensiones fijas de ventana para acceder a acciones principales.
- Los cambios de tamaño deben actualizar el layout sin reiniciar la sesión ni perder la ruta activa.

## Accesibilidad

- Contraste legible conforme a la paleta existente.
- Controles con etiquetas visibles y mensajes de error comprensibles.
- Orden de navegación coherente y áreas táctiles adecuadas.
- Diseño utilizable con zoom del navegador y teclado en los flujos principales.

## Seguridad

- Autenticación JWT contra FastAPI; el frontend no valida credenciales por sí mismo.
- `API_URL` se configura mediante variables de entorno y no se codifican secretos.
- Todas las operaciones protegidas usan el encabezado `Authorization: Bearer` centralizado en `ApiClient`.
- El backend debe publicar únicamente por HTTPS en internet y restringir CORS a los orígenes web autorizados.
- Fotografías y PDF mantienen las validaciones y autorizaciones del backend.
- El cierre de sesión elimina los datos de sesión de Flet.
- No se almacenarán contraseñas ni claves de base de datos en el frontend.

## Criterios de aceptación iniciales

1. La aplicación inicia en navegador mediante un punto de entrada documentado.
2. El login real crea la sesión JWT y abre el dashboard.
3. El menú permite entrar a todos los módulos existentes.
4. Las vistas consumen el backend mediante el `ApiClient` compartido.
5. La interfaz se adapta al menos a anchos de escritorio, tablet y móvil.
6. Android continúa usando su entrada y configuración actuales.
7. Existen pruebas automatizadas básicas del modo web y documentación de ejecución y despliegue.

## Fuera del alcance inicial

- Reemplazar Flet por React, Vue, Svelte o una interfaz HTML/JavaScript separada.
- Cambiar MySQL, FastAPI o las fórmulas clínicas existentes.
- Crear gestión visual de usuarios y roles que hoy no existe.
- Modo sin conexión, sincronización offline o PWA instalable.
- Rediseño de marca o creación de un sistema visual diferente.
- Configuración específica de un proveedor cloud, dominio o certificado productivo.
- Garantizar compatibilidad con navegadores obsoletos.
