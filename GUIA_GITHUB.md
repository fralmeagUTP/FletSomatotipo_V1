# Configuración de GitHub para Somatocarta

Como no tengo acceso directo a tu cuenta de GitHub para crear repositorios, debes seguir estos pasos:

## Paso 1: Crear el Repositorio
1. Ve a [github.com/new](https://github.com/new).
2. Nombre del repositorio: `FletSomatotipo_V1` (o el que prefieras).
3. **NO** marques "Initialize with README", "formatted .gitignore" ni "license". (Ya tenemos esos archivos localmente).
4. Haz clic en **Create repository**.

## Paso 2: Conectar y Subir (Opción A: Lo hago yo por ti)
Una vez creado, copia la **URL HTTPS** del repositorio (ejemplo: `https://github.com/fralmeagUTP/FletSomatotipo_V1.git`) y **envíamela por el chat**.
Yo ejecutaré los comandos necesarios para subir todo.

## Paso 2: Conectar y Subir (Opción B: Hazlo tú mismo)
Si prefieres hacerlo tú, abre una terminal en la carpeta del proyecto y ejecuta:

```bash
git remote add origin <https://github.com/fralmeagUTP/FletSomatotipo_V1.git>
git branch -M main
git push -u origin main
```
