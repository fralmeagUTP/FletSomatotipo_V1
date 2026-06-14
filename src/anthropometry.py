from dataclasses import dataclass


@dataclass(frozen=True)
class MeasurementRule:
    label: str
    minimum_exclusive: float
    maximum_inclusive: float
    unit: str


MEASUREMENT_RULES = {
    "ESTA_USER_CM": MeasurementRule("Estatura", 50, 250, "cm"),
    "PESO_kg": MeasurementRule("Peso", 10, 300, "kg"),
    "PLIEGUE_TRICIPITAL": MeasurementRule("Pliegue tricipital", 0, 100, "mm"),
    "PLIEGUE_SUBESCAPULAR": MeasurementRule("Pliegue subescapular", 0, 100, "mm"),
    "PLIEGUE_SUPRAILIACO": MeasurementRule("Pliegue suprailiaco", 0, 100, "mm"),
    "PLIEGUE_ABDOMINAL": MeasurementRule("Pliegue abdominal", 0, 100, "mm"),
    "PLIEGUE_MUSLO_ANT": MeasurementRule("Pliegue muslo anterior", 0, 100, "mm"),
    "PLIEGUE_MEDIAL_PIERNA": MeasurementRule("Pliegue pierna medial", 0, 100, "mm"),
    "DIAMETRO_BIEPI_MUNECA": MeasurementRule("Diametro muneca", 0, 200, "mm"),
    "DIAMETRO_BIEPI_FEMUR": MeasurementRule("Diametro femur", 0, 200, "mm"),
    "DIAMETRO_CODO": MeasurementRule("Diametro codo", 0, 200, "mm"),
    "PERIMETRO_BICED_CONTRAIDO": MeasurementRule("Perimetro biceps", 0, 250, "cm"),
    "PERIMETRO_PIERNA": MeasurementRule("Perimetro pierna", 0, 250, "cm"),
    "CIRCUNFERENCIA_CARPO": MeasurementRule("Circunferencia carpo", 0, 200, "mm"),
}


def validate_measurement_value(field_name: str, value) -> float:
    rule = MEASUREMENT_RULES[field_name]
    raw_value = str(value or "").strip()
    if not raw_value:
        raise ValueError(f"{rule.label} es obligatorio")
    try:
        parsed_value = float(raw_value.replace(",", "."))
    except ValueError as error:
        raise ValueError(f"{rule.label} debe ser numerico") from error
    if parsed_value <= rule.minimum_exclusive:
        raise ValueError(
            f"{rule.label} debe ser mayor que {rule.minimum_exclusive:g} {rule.unit}"
        )
    if parsed_value > rule.maximum_inclusive:
        raise ValueError(
            f"{rule.label} no puede superar {rule.maximum_inclusive:g} {rule.unit}"
        )
    return parsed_value
