from pathlib import Path


MIGRATION_PATH = Path("scripts/migrations/001_unique_somatotipo_deportista_fecha.sql")


def test_unique_somatotipo_fecha_migration_has_duplicate_guard_and_unique_index():
    sql = MIGRATION_PATH.read_text(encoding="utf-8")

    assert "CDRTablaSomatotipo" in sql
    assert "IDENTI_DEPORTISTA, FECHA_MEDIDA" in sql
    assert "HAVING COUNT(*) > 1" in sql
    assert "SIGNAL SQLSTATE '45000'" in sql
    assert "uq_somatotipo_deportista_fecha" in sql
    assert "UNIQUE (IDENTI_DEPORTISTA, FECHA_MEDIDA)" in sql
    assert "INFORMATION_SCHEMA.STATISTICS" in sql
