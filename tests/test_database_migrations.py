from pathlib import Path


MIGRATION_PATH = Path("scripts/migrations/001_unique_somatotipo_deportista_fecha.sql")
REFERENTIAL_MIGRATION_PATH = Path("scripts/migrations/002_referential_integrity.sql")
RESTRICT_FK_MIGRATION_PATH = Path("scripts/migrations/003_normalize_foreign_keys_restrict.sql")
FORMULA_MIGRATION_PATH = Path("scripts/migrations/004_correct_anthropometric_formulas.sql")


def test_unique_somatotipo_fecha_migration_has_duplicate_guard_and_unique_index():
    sql = MIGRATION_PATH.read_text(encoding="utf-8")

    assert "CDRTablaSomatotipo" in sql
    assert "IDENTI_DEPORTISTA, FECHA_MEDIDA" in sql
    assert "HAVING COUNT(*) > 1" in sql
    assert "SIGNAL SQLSTATE '45000'" in sql
    assert "uq_somatotipo_deportista_fecha" in sql
    assert "UNIQUE (IDENTI_DEPORTISTA, FECHA_MEDIDA)" in sql
    assert "INFORMATION_SCHEMA.STATISTICS" in sql


def test_referential_integrity_migration_guards_data_and_adds_constraints():
    sql = REFERENTIAL_MIGRATION_PATH.read_text(encoding="utf-8")

    assert "SIGNAL SQLSTATE '45000'" in sql
    assert "duplicated_sports" in sql
    assert "duplicated_assignments" in sql
    assert "uq_deporte_nombre" in sql
    assert "uq_asignacion_deporte_deportista_entidad" in sql
    assert "INFORMATION_SCHEMA.KEY_COLUMN_USAGE" in sql
    assert "fk_asignacion_deporte" in sql
    assert "fk_asignacion_deportista" in sql
    assert "fk_asignacion_entidad" in sql
    assert "fk_somatotipo_deportista" in sql
    assert "fk_somatotipo_detalle_encabezado" in sql
    assert sql.count("ON UPDATE RESTRICT ON DELETE RESTRICT") == 5


def test_restrict_fk_migration_replaces_legacy_cascade_rules():
    sql = RESTRICT_FK_MIGRATION_PATH.read_text(encoding="utf-8")

    assert "INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS" in sql
    assert "current_update_rule <> 'RESTRICT'" in sql
    assert "current_delete_rule <> 'RESTRICT'" in sql
    assert "DROP FOREIGN KEY" in sql
    assert "ON UPDATE RESTRICT ON DELETE RESTRICT" in sql
    assert sql.count("CALL ensure_restrict_foreign_key(") == 5
    assert "fk_asignacion_deporte" in sql
    assert "fk_asignacion_deportista" in sql
    assert "fk_asignacion_entidad" in sql
    assert "fk_somatotipo_deportista" in sql
    assert "fk_somatotipo_detalle_encabezado" in sql


def test_formula_migration_normalizes_units_and_replaces_equations():
    sql = FORMULA_MIGRATION_PATH.read_text(encoding="utf-8")

    assert "CDRBackupSomatotipoDetalleFormulaV2" in sql
    assert "DIAMETRO_BIEPI_MUNECA = DIAMETRO_BIEPI_MUNECA * 10" in sql
    assert "ESTA_USER_CM = ESTA_USER_CM * 100" in sql
    assert "CorrectedArmGirthCm" in sql
    assert "CorrectedCalfGirthCm" in sql
    assert "WHEN normalized.HeightWeightRatio >= 40.75" in sql
    assert "WHEN normalized.HeightWeightRatio > 38.25" in sql
    assert "0.213" in sql and "+ 7.9" in sql
    assert "0.1051" in sql and "+ 2.58" in sql
    assert "THEN 0.241 ELSE 0.209" in sql
    assert "CAST(NULL AS DECIMAL(19, 2)) AS PorcGrasoJonson" in sql
    assert "fat.PESO_kg - fat.PesoRasoYuazs" in sql
