import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.backend.database import engine
from src.backend.domain.anthropometry_calculator import (
    faulkner_fat_percent,
    heath_carter_somatotype,
    residual_mass_kg,
    rocha_bone_mass_kg,
    yuhasz_fat_percent,
)


QUERY = """
SELECT id_Somatotipo, ESTA_USER_CM, PESO_kg, SEXO_DEPORTISTA,
       PLIEGUE_TRICIPITAL, PLIEGUE_SUBESCAPULAR, PLIEGUE_SUPRAILIACO,
       PLIEGUE_ABDOMINAL, PLIEGUE_MUSLO_ANT, PLIEGUE_MEDIAL_PIERNA,
       DIAMETRO_BIEPI_MUNECA, DIAMETRO_BIEPI_FEMUR, DIAMETRO_CODO,
       PERIMETRO_BICED_CONTRAIDO, PERIMETRO_PIERNA,
       PorcGrasoFaulker, PorcRasoYuasz, PesoOseo, PesoResidual,
       Endomorfismo, Mesomorfismo, Ectomorfismo, X, Y
FROM CDRVistaValoracionCorporal
ORDER BY id_Somatotipo
"""


def number(row, field):
    value = row[field]
    return float(value) if value is not None else None


def expected_values(row):
    somatotype = heath_carter_somatotype(
        height_cm=number(row, "ESTA_USER_CM"),
        weight_kg=number(row, "PESO_kg"),
        triceps_mm=number(row, "PLIEGUE_TRICIPITAL"),
        subscapular_mm=number(row, "PLIEGUE_SUBESCAPULAR"),
        supraspinale_mm=number(row, "PLIEGUE_SUPRAILIACO"),
        humerus_breadth_mm=number(row, "DIAMETRO_CODO"),
        femur_breadth_mm=number(row, "DIAMETRO_BIEPI_FEMUR"),
        flexed_arm_girth_cm=number(row, "PERIMETRO_BICED_CONTRAIDO"),
        calf_girth_cm=number(row, "PERIMETRO_PIERNA"),
        calf_skinfold_mm=number(row, "PLIEGUE_MEDIAL_PIERNA"),
    )
    fat_inputs = {
        "sex": row["SEXO_DEPORTISTA"],
        "triceps_mm": number(row, "PLIEGUE_TRICIPITAL"),
        "subscapular_mm": number(row, "PLIEGUE_SUBESCAPULAR"),
        "supraspinale_mm": number(row, "PLIEGUE_SUPRAILIACO"),
        "abdominal_mm": number(row, "PLIEGUE_ABDOMINAL"),
    }
    return {
        "Endomorfismo": somatotype.endomorphy,
        "Mesomorfismo": somatotype.mesomorphy,
        "Ectomorfismo": somatotype.ectomorphy,
        "X": somatotype.x,
        "Y": somatotype.y,
        "PesoOseo": rocha_bone_mass_kg(
            number(row, "ESTA_USER_CM"),
            number(row, "DIAMETRO_BIEPI_MUNECA"),
            number(row, "DIAMETRO_BIEPI_FEMUR"),
        ),
        "PesoResidual": residual_mass_kg(number(row, "PESO_kg"), row["SEXO_DEPORTISTA"]),
        "PorcGrasoFaulker": faulkner_fat_percent(**fat_inputs),
        "PorcRasoYuasz": yuhasz_fat_percent(
            **fat_inputs,
            thigh_mm=number(row, "PLIEGUE_MUSLO_ANT"),
            calf_mm=number(row, "PLIEGUE_MEDIAL_PIERNA"),
        ),
    }


def main():
    with engine.connect() as connection:
        rows = connection.execute(text(QUERY)).mappings().all()

    mismatches = []
    for row in rows:
        expected = expected_values(row)
        for field, expected_value in expected.items():
            database_value = number(row, field)
            if database_value is None or abs(database_value - expected_value) > 0.011:
                mismatches.append(
                    f"ID {row['id_Somatotipo']} {field}: DB={database_value} esperado={expected_value:.4f}"
                )

    print(f"Valoraciones verificadas: {len(rows)}")
    if mismatches:
        print(f"Diferencias encontradas: {len(mismatches)}")
        for mismatch in mismatches[:50]:
            print(f"- {mismatch}")
        raise SystemExit(1)
    print("Todas las formulas coinciden con la calculadora de referencia.")


if __name__ == "__main__":
    main()
