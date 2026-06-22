-- Corrige unidades históricas y fórmulas antropométricas.
-- Unidades canónicas: estatura/perímetros/carpo en cm; pliegues/diámetros óseos en mm.

CREATE TABLE IF NOT EXISTS CDRBackupSomatotipoDetalleFormulaV2
LIKE CDRTablaSomatotipoDetalle;

DELIMITER //

DROP PROCEDURE IF EXISTS normalize_anthropometric_units//

CREATE PROCEDURE normalize_anthropometric_units()
BEGIN
    DECLARE ambiguous_rows INT DEFAULT 0;

    SELECT COUNT(*) INTO ambiguous_rows
      FROM CDRTablaSomatotipoDetalle
     WHERE (
            DIAMETRO_BIEPI_MUNECA < 20
         OR DIAMETRO_BIEPI_FEMUR < 20
         OR DIAMETRO_CODO < 20
     )
       AND NOT (
            DIAMETRO_BIEPI_MUNECA < 20
        AND DIAMETRO_BIEPI_FEMUR < 20
        AND DIAMETRO_CODO < 20
       );

    IF ambiguous_rows > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Hay registros con diámetros en escalas mezcladas; deben corregirse manualmente antes de aplicar la migración.';
    END IF;

    INSERT IGNORE INTO CDRBackupSomatotipoDetalleFormulaV2
    SELECT *
      FROM CDRTablaSomatotipoDetalle
     WHERE (
            DIAMETRO_BIEPI_MUNECA BETWEEN 3 AND 19.99
        AND DIAMETRO_BIEPI_FEMUR BETWEEN 3 AND 19.99
        AND DIAMETRO_CODO BETWEEN 3 AND 19.99
     )
        OR ESTA_USER_CM BETWEEN 1 AND 3;

    UPDATE CDRTablaSomatotipoDetalle
       SET DIAMETRO_BIEPI_MUNECA = DIAMETRO_BIEPI_MUNECA * 10,
           DIAMETRO_BIEPI_FEMUR = DIAMETRO_BIEPI_FEMUR * 10,
           DIAMETRO_CODO = DIAMETRO_CODO * 10
     WHERE DIAMETRO_BIEPI_MUNECA BETWEEN 3 AND 19.99
       AND DIAMETRO_BIEPI_FEMUR BETWEEN 3 AND 19.99
       AND DIAMETRO_CODO BETWEEN 3 AND 19.99;

    UPDATE CDRTablaSomatotipoDetalle
       SET ESTA_USER_CM = ESTA_USER_CM * 100
     WHERE ESTA_USER_CM BETWEEN 1 AND 3;
END//

CALL normalize_anthropometric_units()//
DROP PROCEDURE normalize_anthropometric_units//

DELIMITER ;

CREATE OR REPLACE VIEW CDRVistaSomatotipo AS
SELECT
    calculated.id_Somatotipo,
    calculated.IDENTI_DEPORTISTA,
    calculated.NOMBRE_DEPORTISTA,
    calculated.SEXO_DEPORTISTA,
    calculated.EDAD,
    calculated.FECHA_MEDIDA,
    calculated.PESO_kg,
    calculated.ESTA_USER_CM,
    calculated.DIAMETRO_CODO,
    calculated.DIAMETRO_BIEPI_FEMUR,
    calculated.PERIMETRO_BICED_CONTRAIDO,
    calculated.PERIMETRO_PIERNA,
    calculated.PLIEGUE_SUBESCAPULAR,
    calculated.PLIEGUE_TRICIPITAL,
    calculated.PLIEGUE_SUPRAILIACO,
    calculated.PLIEGUE_ABDOMINAL,
    calculated.PLIEGUE_MUSLO_ANT,
    calculated.PLIEGUE_MEDIAL_PIERNA,
    ROUND(calculated.PESO_kg / POW(calculated.ESTA_USER_CM / 100, 2), 2) AS IMC,
    ROUND(calculated.CorrectedSkinfoldSum, 2) AS Xc,
    ROUND(POW(calculated.CorrectedSkinfoldSum, 2), 2) AS Xc2,
    ROUND(POW(calculated.CorrectedSkinfoldSum, 3), 2) AS Xc3,
    ROUND(calculated.HeightWeightRatio, 2) AS Hwr,
    ROUND(calculated.EndomorphyRaw, 2) AS Endomorfismo,
    ROUND(calculated.MesomorphyRaw, 2) AS Mesomorfismo,
    ROUND(calculated.EctomorphyRaw, 2) AS Ectomorfismo,
    ROUND(calculated.EctomorphyRaw - calculated.EndomorphyRaw, 2) AS X,
    ROUND(2 * calculated.MesomorphyRaw - calculated.EndomorphyRaw - calculated.EctomorphyRaw, 2) AS Y
FROM (
    SELECT
        normalized.*,
        -0.7182
            + 0.1451 * normalized.CorrectedSkinfoldSum
            - 0.00068 * POW(normalized.CorrectedSkinfoldSum, 2)
            + 0.0000014 * POW(normalized.CorrectedSkinfoldSum, 3) AS EndomorphyRaw,
        0.858 * normalized.HumerusBreadthCm
            + 0.601 * normalized.FemurBreadthCm
            + 0.188 * normalized.CorrectedArmGirthCm
            + 0.161 * normalized.CorrectedCalfGirthCm
            - 0.131 * normalized.ESTA_USER_CM
            + 4.5 AS MesomorphyRaw,
        CASE
            WHEN normalized.HeightWeightRatio >= 40.75
                THEN 0.732 * normalized.HeightWeightRatio - 28.58
            WHEN normalized.HeightWeightRatio > 38.25
                THEN 0.463 * normalized.HeightWeightRatio - 17.63
            ELSE 0.1
        END AS EctomorphyRaw
    FROM (
        SELECT
            detail.*,
            (detail.PLIEGUE_SUBESCAPULAR + detail.PLIEGUE_TRICIPITAL + detail.PLIEGUE_SUPRAILIACO)
                * 170.18 / detail.ESTA_USER_CM AS CorrectedSkinfoldSum,
            detail.ESTA_USER_CM / POW(detail.PESO_kg, 1 / 3) AS HeightWeightRatio,
            detail.DIAMETRO_CODO / 10 AS HumerusBreadthCm,
            detail.DIAMETRO_BIEPI_FEMUR / 10 AS FemurBreadthCm,
            detail.PERIMETRO_BICED_CONTRAIDO - detail.PLIEGUE_TRICIPITAL / 10 AS CorrectedArmGirthCm,
            detail.PERIMETRO_PIERNA - detail.PLIEGUE_MEDIAL_PIERNA / 10 AS CorrectedCalfGirthCm
        FROM CDRVistaSomatotipoDetalle detail
    ) normalized
) calculated;

CREATE OR REPLACE VIEW CDRVistaPesoGraso AS
SELECT
    detail.id_Somatotipo,
    detail.IDENTI_DEPORTISTA,
    detail.NOMBRE_DEPORTISTA,
    detail.FECHA_MEDIDA,
    detail.ESTA_USER_CM,
    detail.PESO_kg,
    detail.EDAD,
    detail.PLIEGUE_TRICIPITAL,
    detail.PLIEGUE_SUBESCAPULAR,
    detail.PLIEGUE_SUPRAILIACO,
    detail.PLIEGUE_ABDOMINAL,
    detail.PLIEGUE_MUSLO_ANT,
    detail.PLIEGUE_MEDIAL_PIERNA,
    CAST(NULL AS DECIMAL(19, 2)) AS PorcGrasoJonson,
    CAST(NULL AS DECIMAL(25, 2)) AS PesoGrasoJhonston,
    ROUND(
        CASE
            WHEN UPPER(detail.SEXO_DEPORTISTA) = 'M' THEN
                0.153 * (
                    detail.PLIEGUE_ABDOMINAL + detail.PLIEGUE_SUPRAILIACO
                    + detail.PLIEGUE_SUBESCAPULAR + detail.PLIEGUE_TRICIPITAL
                ) + 5.783
            ELSE
                0.213 * (
                    detail.PLIEGUE_ABDOMINAL + detail.PLIEGUE_SUPRAILIACO
                    + detail.PLIEGUE_SUBESCAPULAR + detail.PLIEGUE_TRICIPITAL
                ) + 7.9
        END,
        2
    ) AS PorcGrasoFaulker,
    ROUND(
        detail.PESO_kg * (
            CASE
                WHEN UPPER(detail.SEXO_DEPORTISTA) = 'M' THEN
                    0.153 * (
                        detail.PLIEGUE_ABDOMINAL + detail.PLIEGUE_SUPRAILIACO
                        + detail.PLIEGUE_SUBESCAPULAR + detail.PLIEGUE_TRICIPITAL
                    ) + 5.783
                ELSE
                    0.213 * (
                        detail.PLIEGUE_ABDOMINAL + detail.PLIEGUE_SUPRAILIACO
                        + detail.PLIEGUE_SUBESCAPULAR + detail.PLIEGUE_TRICIPITAL
                    ) + 7.9
            END
        ) / 100,
        2
    ) AS PesoRasoFaulker,
    ROUND(
        CASE
            WHEN UPPER(detail.SEXO_DEPORTISTA) = 'M' THEN
                0.1051 * (
                    detail.PLIEGUE_MEDIAL_PIERNA + detail.PLIEGUE_MUSLO_ANT
                    + detail.PLIEGUE_SUBESCAPULAR + detail.PLIEGUE_SUPRAILIACO
                    + detail.PLIEGUE_ABDOMINAL + detail.PLIEGUE_TRICIPITAL
                ) + 2.58
            ELSE
                0.1548 * (
                    detail.PLIEGUE_MEDIAL_PIERNA + detail.PLIEGUE_MUSLO_ANT
                    + detail.PLIEGUE_SUBESCAPULAR + detail.PLIEGUE_SUPRAILIACO
                    + detail.PLIEGUE_ABDOMINAL + detail.PLIEGUE_TRICIPITAL
                ) + 3.58
        END,
        2
    ) AS PorcRasoYuasz,
    ROUND(
        detail.PESO_kg * (
            CASE
                WHEN UPPER(detail.SEXO_DEPORTISTA) = 'M' THEN
                    0.1051 * (
                        detail.PLIEGUE_MEDIAL_PIERNA + detail.PLIEGUE_MUSLO_ANT
                        + detail.PLIEGUE_SUBESCAPULAR + detail.PLIEGUE_SUPRAILIACO
                        + detail.PLIEGUE_ABDOMINAL + detail.PLIEGUE_TRICIPITAL
                    ) + 2.58
                ELSE
                    0.1548 * (
                        detail.PLIEGUE_MEDIAL_PIERNA + detail.PLIEGUE_MUSLO_ANT
                        + detail.PLIEGUE_SUBESCAPULAR + detail.PLIEGUE_SUPRAILIACO
                        + detail.PLIEGUE_ABDOMINAL + detail.PLIEGUE_TRICIPITAL
                    ) + 3.58
            END
        ) / 100,
        2
    ) AS PesoRasoYuazs
FROM CDRVistaSomatotipoDetalle detail;

CREATE OR REPLACE VIEW CDRVistaPesoResidual AS
SELECT
    detail.id_Somatotipo,
    detail.IDENTI_DEPORTISTA,
    detail.NOMBRE_DEPORTISTA,
    detail.FECHA_MEDIDA,
    detail.PESO_kg,
    ROUND(
        detail.PESO_kg * CASE WHEN UPPER(detail.SEXO_DEPORTISTA) = 'M' THEN 0.241 ELSE 0.209 END,
        2
    ) AS PesoResidual
FROM CDRVistaSomatotipoDetalle detail;

CREATE OR REPLACE VIEW CDRVistaPesoOseo AS
SELECT
    detail.id_Somatotipo,
    detail.IDENTI_DEPORTISTA,
    detail.NOMBRE_DEPORTISTA,
    detail.FECHA_MEDIDA,
    detail.ESTA_USER_CM,
    detail.DIAMETRO_BIEPI_MUNECA,
    detail.DIAMETRO_BIEPI_FEMUR,
    ROUND(
        3.02 * POW(
            POW(detail.ESTA_USER_CM / 100, 2)
            * (detail.DIAMETRO_BIEPI_MUNECA / 1000)
            * (detail.DIAMETRO_BIEPI_FEMUR / 1000)
            * 400,
            0.712
        ),
        2
    ) AS PesoOseo
FROM CDRVistaSomatotipoDetalle detail;

CREATE OR REPLACE VIEW CDRVistaMMA AS
SELECT
    fat.id_Somatotipo,
    fat.IDENTI_DEPORTISTA,
    fat.NOMBRE_DEPORTISTA,
    fat.FECHA_MEDIDA,
    fat.PESO_kg,
    bone.PesoOseo,
    ROUND(fat.PesoRasoYuazs, 2) AS PesoRasoYuazs,
    residual.PesoResidual,
    ROUND(fat.PESO_kg - fat.PesoRasoYuazs - bone.PesoOseo - residual.PesoResidual, 2) AS Mma
FROM CDRVistaPesoGraso fat
JOIN CDRVistaPesoOseo bone ON fat.id_Somatotipo = bone.id_Somatotipo
JOIN CDRVistaPesoResidual residual ON fat.id_Somatotipo = residual.id_Somatotipo;

DELIMITER //

DROP FUNCTION IF EXISTS FUNC_ESCALAECTOMORFISMO//

CREATE FUNCTION FUNC_ESCALAECTOMORFISMO(Valor_Ectomorfismo FLOAT)
RETURNS LONGTEXT CHARSET utf8mb4
NO SQL
BEGIN
    DECLARE texto LONGTEXT;
    IF Valor_Ectomorfismo <= 2.9 THEN
        SET texto = 'BAJO: Baja linealidad relativa, mayor volumen corporal por unidad de altura.';
    ELSEIF Valor_Ectomorfismo <= 4.9 THEN
        SET texto = 'MODERADO: Linealidad relativa moderada, menor volumen por unidad de altura.';
    ELSEIF Valor_Ectomorfismo <= 6.9 THEN
        SET texto = 'ALTO: Linealidad relativa elevada y poco volumen por unidad de altura.';
    ELSE
        SET texto = 'MUY ALTO: Linealidad relativa extremadamente alta, cuerpo muy alargado y volumen mínimo por unidad de altura.';
    END IF;
    RETURN texto;
END//

DELIMITER ;
