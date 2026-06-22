-- Normaliza claves foráneas heredadas para que usen RESTRICT en actualización y eliminación.
-- Detecta las restricciones por tabla y columna, incluso si MySQL les asignó nombres automáticos.

DELIMITER //

DROP PROCEDURE IF EXISTS ensure_restrict_foreign_key//

CREATE PROCEDURE ensure_restrict_foreign_key(
    IN source_table VARCHAR(64),
    IN source_column VARCHAR(64),
    IN target_table VARCHAR(64),
    IN target_column VARCHAR(64),
    IN desired_constraint VARCHAR(64)
)
BEGIN
    DECLARE current_constraint VARCHAR(64) DEFAULT NULL;
    DECLARE current_update_rule VARCHAR(30) DEFAULT NULL;
    DECLARE current_delete_rule VARCHAR(30) DEFAULT NULL;

    SELECT k.CONSTRAINT_NAME, r.UPDATE_RULE, r.DELETE_RULE
      INTO current_constraint, current_update_rule, current_delete_rule
      FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE k
      JOIN INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS r
        ON r.CONSTRAINT_SCHEMA = k.CONSTRAINT_SCHEMA
       AND r.TABLE_NAME = k.TABLE_NAME
       AND r.CONSTRAINT_NAME = k.CONSTRAINT_NAME
     WHERE k.TABLE_SCHEMA = DATABASE()
       AND k.TABLE_NAME = source_table
       AND k.COLUMN_NAME = source_column
       AND k.REFERENCED_TABLE_NAME = target_table
       AND k.REFERENCED_COLUMN_NAME = target_column
     LIMIT 1;

    IF current_constraint IS NOT NULL
       AND (current_update_rule <> 'RESTRICT' OR current_delete_rule <> 'RESTRICT') THEN
        SET @drop_foreign_key = CONCAT(
            'ALTER TABLE `', source_table,
            '` DROP FOREIGN KEY `', current_constraint, '`'
        );
        PREPARE drop_statement FROM @drop_foreign_key;
        EXECUTE drop_statement;
        DEALLOCATE PREPARE drop_statement;
        SET current_constraint = NULL;
    END IF;

    IF current_constraint IS NULL THEN
        SET @add_foreign_key = CONCAT(
            'ALTER TABLE `', source_table,
            '` ADD CONSTRAINT `', desired_constraint,
            '` FOREIGN KEY (`', source_column,
            '`) REFERENCES `', target_table,
            '` (`', target_column,
            '`) ON UPDATE RESTRICT ON DELETE RESTRICT'
        );
        PREPARE add_statement FROM @add_foreign_key;
        EXECUTE add_statement;
        DEALLOCATE PREPARE add_statement;
    END IF;
END//

CALL ensure_restrict_foreign_key(
    'CDRTablaDeportesDeportistas', 'ID_DEPORTE',
    'CDRTablaDeportes', 'ID_DEPORTE',
    'fk_asignacion_deporte'
)//

CALL ensure_restrict_foreign_key(
    'CDRTablaDeportesDeportistas', 'IDENTI_DEPORTISTA',
    'CDRTablaDeportistas', 'IDENTI_DEPORTISTA',
    'fk_asignacion_deportista'
)//

CALL ensure_restrict_foreign_key(
    'CDRTablaDeportesDeportistas', 'NIT_ENTIDAD',
    'CDRTablaEntidades', 'NIT_ENTIDAD',
    'fk_asignacion_entidad'
)//

CALL ensure_restrict_foreign_key(
    'CDRTablaSomatotipo', 'IDENTI_DEPORTISTA',
    'CDRTablaDeportistas', 'IDENTI_DEPORTISTA',
    'fk_somatotipo_deportista'
)//

CALL ensure_restrict_foreign_key(
    'CDRTablaSomatotipoDetalle', 'id_Somatotipo',
    'CDRTablaSomatotipo', 'id_Somatotipo',
    'fk_somatotipo_detalle_encabezado'
)//

DROP PROCEDURE ensure_restrict_foreign_key//

DELIMITER ;
