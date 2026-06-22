# Integridad referencial

## Política

Somatocarta usa una política `RESTRICT`: un registro padre no se elimina mientras tenga datos dependientes.

| Registro | Dependencias que bloquean la eliminación |
|----------|------------------------------------------|
| Deportista | Asignaciones deportivas o valoraciones corporales |
| Entidad | Asignaciones deportivas |
| Deporte | Asignaciones deportivas |

Las asignaciones se pueden eliminar directamente. Las valoraciones completas se eliminan mediante su flujo específico, que elimina primero sus detalles.

La API responde `409 Conflict` cuando una operación viola estas reglas. El mensaje indica cuántas dependencias existen y cuáles deben eliminarse primero.

## Reglas adicionales

- `IDENTI_DEPORTISTA` y `NIT_ENTIDAD` son identificadores inmutables.
- El nombre de un deporte debe ser único sin distinguir mayúsculas de minúsculas.
- La combinación deporte, deportista y entidad debe ser única por asignación.
- Toda asignación debe referenciar un deporte, deportista y entidad existentes.
- Toda valoración debe referenciar un deportista existente.
- Todo detalle debe referenciar una valoración existente.

## Migración MySQL

Después de desplegar el código, ejecutar:

```powershell
cmd /c "mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p %DB_NAME% < scripts\migrations\002_referential_integrity.sql"
```

La migración inspecciona primero los datos. Si encuentra deportes o asignaciones duplicadas, referencias huérfanas o relaciones incompletas, se detiene con `SQLSTATE 45000` sin agregar restricciones. Los datos reportados deben corregirse antes de repetirla.

Cuando la validación termina correctamente, se crean índices únicos y claves foráneas con `ON UPDATE RESTRICT` y `ON DELETE RESTRICT`.

Si la base ya tenía claves foráneas heredadas con reglas `CASCADE`, ejecutar también:

```powershell
cmd /c "mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p %DB_NAME% < scripts\migrations\003_normalize_foreign_keys_restrict.sql"
```

La migración `003` detecta las restricciones por tabla y columna, elimina únicamente las que usan reglas diferentes y las recrea con `ON UPDATE RESTRICT` y `ON DELETE RESTRICT`.

## Estado de la base activa

Al 21 de junio de 2026, las restricciones de integridad referencial y la política `RESTRICT` están aplicadas y verificadas en la base MySQL activa. Las eliminaciones dependientes también se bloquean en la API con HTTP 409 y las pantallas solicitan confirmación antes de eliminar.
