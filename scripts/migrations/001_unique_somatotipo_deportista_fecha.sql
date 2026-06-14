-- Garantiza una sola valoración por deportista y fecha.
-- Ejecutar contra la base de datos de Somatocarta seleccionada.
-- Si ya existen duplicados, la migración falla sin crear el índice.

DELIMITER //

DROP PROCEDURE IF EXISTS apply_somatotipo_unique_fecha//

CREATE PROCEDURE apply_somatotipo_unique_fecha()
BEGIN
    DECLARE duplicate_groups INT DEFAULT 0;
    DECLARE index_exists INT DEFAULT 0;

    SELECT COUNT(*)
      INTO duplicate_groups
      FROM (
            SELECT IDENTI_DEPORTISTA, FECHA_MEDIDA
              FROM CDRTablaSomatotipo
             WHERE IDENTI_DEPORTISTA IS NOT NULL
               AND FECHA_MEDIDA IS NOT NULL
             GROUP BY IDENTI_DEPORTISTA, FECHA_MEDIDA
            HAVING COUNT(*) > 1
      ) AS duplicated_somatotipos;

    IF duplicate_groups > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Existen valoraciones duplicadas por deportista y fecha; depure los datos antes de crear uq_somatotipo_deportista_fecha.';
    END IF;

    SELECT COUNT(*)
      INTO index_exists
      FROM INFORMATION_SCHEMA.STATISTICS
     WHERE TABLE_SCHEMA = DATABASE()
       AND TABLE_NAME = 'CDRTablaSomatotipo'
       AND INDEX_NAME = 'uq_somatotipo_deportista_fecha'
       AND NON_UNIQUE = 0;

    IF index_exists = 0 THEN
        ALTER TABLE CDRTablaSomatotipo
            ADD CONSTRAINT uq_somatotipo_deportista_fecha
            UNIQUE (IDENTI_DEPORTISTA, FECHA_MEDIDA);
    END IF;
END//

CALL apply_somatotipo_unique_fecha()//

DROP PROCEDURE apply_somatotipo_unique_fecha//

DELIMITER ;
