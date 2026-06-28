-- Crea la tabla para registrar la valoracion deportiva aplicada a funcionarios/deportistas
-- que representan a la UTP en eventos deportivos.
--
-- Relacion principal:
--   CDRTablaDeportistas.IDENTI_DEPORTISTA
--       1 -> N
--   CDRTablaValoracionDeportiva.IDENTI_DEPORTISTA

CREATE TABLE IF NOT EXISTS CDRTablaValoracionDeportiva (
    ID_VALORACION_DEPORTIVA INT AUTO_INCREMENT PRIMARY KEY,

    IDENTI_DEPORTISTA VARCHAR(20) NOT NULL,
    FECHA_PRUEBA DATE NOT NULL,
    LOGIN_USER VARCHAR(60) NULL,

    -- Antropometria basica
    TALLA_M DECIMAL(5, 2) NULL,
    PESO_KG DECIMAL(6, 2) NULL,
    IMC DECIMAL(5, 2) GENERATED ALWAYS AS (
        CASE
            WHEN TALLA_M IS NULL OR TALLA_M <= 0 OR PESO_KG IS NULL THEN NULL
            ELSE ROUND(PESO_KG / (TALLA_M * TALLA_M), 2)
        END
    ) STORED,
    IMC_VALORACION VARCHAR(80) NULL,
    PERIMETRO_ABDOMINAL_CM DECIMAL(6, 2) NULL,
    PERIMETRO_ABDOMINAL_VALORACION VARCHAR(80) NULL,
    PORC_GRASA_CORPORAL DECIMAL(5, 2) NULL,
    MASA_GRASA_KG DECIMAL(6, 2) GENERATED ALWAYS AS (
        CASE
            WHEN PESO_KG IS NULL OR PORC_GRASA_CORPORAL IS NULL THEN NULL
            ELSE ROUND(PESO_KG * PORC_GRASA_CORPORAL / 100, 2)
        END
    ) STORED,
    MASA_LIBRE_GRASA_KG DECIMAL(6, 2) GENERATED ALWAYS AS (
        CASE
            WHEN PESO_KG IS NULL OR PORC_GRASA_CORPORAL IS NULL THEN NULL
            ELSE ROUND(PESO_KG * (1 - PORC_GRASA_CORPORAL / 100), 2)
        END
    ) STORED,
    AKS DECIMAL(6, 2) GENERATED ALWAYS AS (
        CASE
            WHEN TALLA_M IS NULL
              OR TALLA_M <= 0
              OR PESO_KG IS NULL
              OR PORC_GRASA_CORPORAL IS NULL THEN NULL
            ELSE ROUND((PESO_KG * (1 - PORC_GRASA_CORPORAL / 100)) / (TALLA_M * TALLA_M), 2)
        END
    ) STORED,
    AKS_VALORACION VARCHAR(80) NULL,
    GRASA_CORPORAL_VALORACION VARCHAR(80) NULL,

    -- Fuerza
    FUERZA_PRENSIL_D DECIMAL(6, 2) NULL,
    FUERZA_PRENSIL_I DECIMAL(6, 2) NULL,
    FUERZA_PRENSIL_VALORACION VARCHAR(80) NULL,
    PESO_MUERTO_KG DECIMAL(6, 2) NULL,
    PESO_MUERTO_VALORACION VARCHAR(80) NULL,
    CORE_ANTERIOR_SEG DECIMAL(6, 2) NULL,
    CORE_ANTERIOR_VALORACION VARCHAR(80) NULL,
    CORE_POSTERIOR_SEG DECIMAL(6, 2) NULL,
    CORE_POSTERIOR_VALORACION VARCHAR(80) NULL,

    -- Resistencia: Test del banco Queen College
    FC_REPOSO INT NULL,
    FC_MAXIMA INT NULL,
    FC_REC_15S INT NULL,
    FC_REC_1M INT NULL,
    FC_REC_3M INT NULL,
    VO2_MAX DECIMAL(6, 2) NULL,
    VO2_MAX_VALORACION VARCHAR(80) NULL,

    -- Flexibilidad y movilidad
    FLEXIBILIDAD_PUNTUACION DECIMAL(6, 2) NULL,
    FLEXIBILIDAD_VALORACION VARCHAR(80) NULL,
    MOVILIDAD_FMS_PUNTUACION DECIMAL(6, 2) NULL,
    MOVILIDAD_FMS_VALORACION VARCHAR(80) NULL,

    OBSERVACIONES TEXT NULL,
    CREATED_AT DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT DATETIME NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_valoracion_deportiva_deportista_fecha
        UNIQUE (IDENTI_DEPORTISTA, FECHA_PRUEBA)
) ENGINE=InnoDB;

DELIMITER //

DROP PROCEDURE IF EXISTS apply_valoracion_deportiva_fk//

CREATE PROCEDURE apply_valoracion_deportiva_fk()
BEGIN
    DECLARE parent_column_type TEXT DEFAULT NULL;
    DECLARE parent_charset VARCHAR(64) DEFAULT NULL;
    DECLARE parent_collation VARCHAR(64) DEFAULT NULL;
    DECLARE parent_engine VARCHAR(64) DEFAULT NULL;
    DECLARE parent_indexed INT DEFAULT 0;
    DECLARE fk_exists INT DEFAULT 0;

    SELECT c.COLUMN_TYPE, c.CHARACTER_SET_NAME, c.COLLATION_NAME, t.ENGINE
      INTO parent_column_type, parent_charset, parent_collation, parent_engine
      FROM INFORMATION_SCHEMA.COLUMNS c
      JOIN INFORMATION_SCHEMA.TABLES t
        ON t.TABLE_SCHEMA = c.TABLE_SCHEMA
       AND t.TABLE_NAME = c.TABLE_NAME
     WHERE c.TABLE_SCHEMA = DATABASE()
       AND c.TABLE_NAME = 'CDRTablaDeportistas'
       AND c.COLUMN_NAME = 'IDENTI_DEPORTISTA'
     LIMIT 1;

    IF parent_column_type IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No existe CDRTablaDeportistas.IDENTI_DEPORTISTA; cree la tabla padre antes de esta migracion.';
    END IF;

    IF UPPER(parent_engine) <> 'INNODB' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'CDRTablaDeportistas debe usar ENGINE=InnoDB para crear la clave foranea.';
    END IF;

    SELECT COUNT(*) INTO parent_indexed
      FROM INFORMATION_SCHEMA.STATISTICS
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'CDRTablaDeportistas'
       AND COLUMN_NAME = 'IDENTI_DEPORTISTA'
       AND SEQ_IN_INDEX = 1;

    IF parent_indexed = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'CDRTablaDeportistas.IDENTI_DEPORTISTA debe estar indexada o ser PRIMARY KEY.';
    END IF;

    SET @alter_valoracion_deportiva_ident = CONCAT(
        'ALTER TABLE `CDRTablaValoracionDeportiva` MODIFY `IDENTI_DEPORTISTA` ',
        parent_column_type,
        IF(parent_charset IS NULL, '', CONCAT(' CHARACTER SET ', parent_charset)),
        IF(parent_collation IS NULL, '', CONCAT(' COLLATE ', parent_collation)),
        ' NOT NULL'
    );
    PREPARE alter_valoracion_deportiva_ident FROM @alter_valoracion_deportiva_ident;
    EXECUTE alter_valoracion_deportiva_ident;
    DEALLOCATE PREPARE alter_valoracion_deportiva_ident;

    SELECT COUNT(*) INTO fk_exists
      FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'CDRTablaValoracionDeportiva'
       AND CONSTRAINT_NAME = 'fk_valoracion_deportiva_deportista';

    IF fk_exists = 0 THEN
        ALTER TABLE CDRTablaValoracionDeportiva
            ADD CONSTRAINT fk_valoracion_deportiva_deportista
            FOREIGN KEY (IDENTI_DEPORTISTA)
            REFERENCES CDRTablaDeportistas (IDENTI_DEPORTISTA)
            ON UPDATE RESTRICT
            ON DELETE RESTRICT;
    END IF;
END//

CALL apply_valoracion_deportiva_fk()//

DROP PROCEDURE apply_valoracion_deportiva_fk//

DELIMITER ;
