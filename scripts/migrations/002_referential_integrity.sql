-- Protege las relaciones entre deportistas, entidades, deportes, asignaciones y valoraciones.
-- La migración se detiene sin modificar el esquema si encuentra datos huérfanos o duplicados.

DELIMITER //

DROP PROCEDURE IF EXISTS apply_referential_integrity//

CREATE PROCEDURE apply_referential_integrity()
BEGIN
    DECLARE invalid_rows INT DEFAULT 0;
    DECLARE object_exists INT DEFAULT 0;

    SELECT COUNT(*) INTO invalid_rows
      FROM CDRTablaDeportes
     WHERE DEPORTE IS NULL OR TRIM(DEPORTE) = '';
    IF invalid_rows > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Existen deportes sin nombre; corrija los datos antes de aplicar integridad referencial.';
    END IF;

    SELECT COUNT(*) INTO invalid_rows
      FROM (
            SELECT LOWER(TRIM(DEPORTE))
              FROM CDRTablaDeportes
             GROUP BY LOWER(TRIM(DEPORTE))
            HAVING COUNT(*) > 1
      ) AS duplicated_sports;
    IF invalid_rows > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Existen deportes duplicados; unifique los registros antes de crear uq_deporte_nombre.';
    END IF;

    SELECT COUNT(*) INTO invalid_rows
      FROM (
            SELECT ID_DEPORTE, IDENTI_DEPORTISTA, NIT_ENTIDAD
              FROM CDRTablaDeportesDeportistas
             GROUP BY ID_DEPORTE, IDENTI_DEPORTISTA, NIT_ENTIDAD
            HAVING COUNT(*) > 1
      ) AS duplicated_assignments;
    IF invalid_rows > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Existen asignaciones duplicadas; depure los datos antes de crear la restricción única.';
    END IF;

    SELECT COUNT(*) INTO invalid_rows
      FROM CDRTablaDeportesDeportistas a
     WHERE a.ID_DEPORTE IS NULL
        OR a.IDENTI_DEPORTISTA IS NULL
        OR a.NIT_ENTIDAD IS NULL
        OR NOT EXISTS (
            SELECT 1 FROM CDRTablaDeportes sport
             WHERE sport.ID_DEPORTE = a.ID_DEPORTE
        )
        OR NOT EXISTS (
            SELECT 1 FROM CDRTablaDeportistas athlete
             WHERE athlete.IDENTI_DEPORTISTA = a.IDENTI_DEPORTISTA
        )
        OR NOT EXISTS (
            SELECT 1 FROM CDRTablaEntidades entity
             WHERE entity.NIT_ENTIDAD = a.NIT_ENTIDAD
        );
    IF invalid_rows > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Existen asignaciones huérfanas o incompletas; corríjalas antes de aplicar claves foráneas.';
    END IF;

    SELECT COUNT(*) INTO invalid_rows
      FROM CDRTablaSomatotipo valuation
     WHERE valuation.IDENTI_DEPORTISTA IS NULL
        OR NOT EXISTS (
            SELECT 1 FROM CDRTablaDeportistas athlete
             WHERE athlete.IDENTI_DEPORTISTA = valuation.IDENTI_DEPORTISTA
        );
    IF invalid_rows > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Existen valoraciones sin deportista válido; corríjalas antes de aplicar la clave foránea.';
    END IF;

    SELECT COUNT(*) INTO invalid_rows
      FROM CDRTablaSomatotipoDetalle detail
     WHERE detail.id_Somatotipo IS NULL
        OR NOT EXISTS (
            SELECT 1 FROM CDRTablaSomatotipo valuation
             WHERE valuation.id_Somatotipo = detail.id_Somatotipo
        );
    IF invalid_rows > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Existen detalles de valoración huérfanos; corríjalos antes de aplicar la clave foránea.';
    END IF;

    SELECT COUNT(*) INTO object_exists
      FROM INFORMATION_SCHEMA.STATISTICS
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'CDRTablaDeportes'
       AND INDEX_NAME = 'uq_deporte_nombre'
       AND NON_UNIQUE = 0;
    IF object_exists = 0 THEN
        ALTER TABLE CDRTablaDeportes
            ADD CONSTRAINT uq_deporte_nombre UNIQUE (DEPORTE);
    END IF;

    SELECT COUNT(*) INTO object_exists
      FROM INFORMATION_SCHEMA.STATISTICS
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'CDRTablaDeportesDeportistas'
       AND INDEX_NAME = 'uq_asignacion_deporte_deportista_entidad'
       AND NON_UNIQUE = 0;
    IF object_exists = 0 THEN
        ALTER TABLE CDRTablaDeportesDeportistas
            ADD CONSTRAINT uq_asignacion_deporte_deportista_entidad
            UNIQUE (ID_DEPORTE, IDENTI_DEPORTISTA, NIT_ENTIDAD);
    END IF;

    SELECT COUNT(*) INTO object_exists
      FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'CDRTablaDeportesDeportistas'
       AND COLUMN_NAME = 'ID_DEPORTE'
       AND REFERENCED_TABLE_NAME = 'CDRTablaDeportes';
    IF object_exists = 0 THEN
        ALTER TABLE CDRTablaDeportesDeportistas
            ADD CONSTRAINT fk_asignacion_deporte
            FOREIGN KEY (ID_DEPORTE) REFERENCES CDRTablaDeportes(ID_DEPORTE)
            ON UPDATE RESTRICT ON DELETE RESTRICT;
    END IF;

    SELECT COUNT(*) INTO object_exists
      FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'CDRTablaDeportesDeportistas'
       AND COLUMN_NAME = 'IDENTI_DEPORTISTA'
       AND REFERENCED_TABLE_NAME = 'CDRTablaDeportistas';
    IF object_exists = 0 THEN
        ALTER TABLE CDRTablaDeportesDeportistas
            ADD CONSTRAINT fk_asignacion_deportista
            FOREIGN KEY (IDENTI_DEPORTISTA) REFERENCES CDRTablaDeportistas(IDENTI_DEPORTISTA)
            ON UPDATE RESTRICT ON DELETE RESTRICT;
    END IF;

    SELECT COUNT(*) INTO object_exists
      FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'CDRTablaDeportesDeportistas'
       AND COLUMN_NAME = 'NIT_ENTIDAD'
       AND REFERENCED_TABLE_NAME = 'CDRTablaEntidades';
    IF object_exists = 0 THEN
        ALTER TABLE CDRTablaDeportesDeportistas
            ADD CONSTRAINT fk_asignacion_entidad
            FOREIGN KEY (NIT_ENTIDAD) REFERENCES CDRTablaEntidades(NIT_ENTIDAD)
            ON UPDATE RESTRICT ON DELETE RESTRICT;
    END IF;

    SELECT COUNT(*) INTO object_exists
      FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'CDRTablaSomatotipo'
       AND COLUMN_NAME = 'IDENTI_DEPORTISTA'
       AND REFERENCED_TABLE_NAME = 'CDRTablaDeportistas';
    IF object_exists = 0 THEN
        ALTER TABLE CDRTablaSomatotipo
            ADD CONSTRAINT fk_somatotipo_deportista
            FOREIGN KEY (IDENTI_DEPORTISTA) REFERENCES CDRTablaDeportistas(IDENTI_DEPORTISTA)
            ON UPDATE RESTRICT ON DELETE RESTRICT;
    END IF;

    SELECT COUNT(*) INTO object_exists
      FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'CDRTablaSomatotipoDetalle'
       AND COLUMN_NAME = 'id_Somatotipo'
       AND REFERENCED_TABLE_NAME = 'CDRTablaSomatotipo';
    IF object_exists = 0 THEN
        ALTER TABLE CDRTablaSomatotipoDetalle
            ADD CONSTRAINT fk_somatotipo_detalle_encabezado
            FOREIGN KEY (id_Somatotipo) REFERENCES CDRTablaSomatotipo(id_Somatotipo)
            ON UPDATE RESTRICT ON DELETE RESTRICT;
    END IF;
END//

CALL apply_referential_integrity()//

DROP PROCEDURE apply_referential_integrity//

DELIMITER ;
