from decimal import Decimal, InvalidOperation


def parse_float(value):
    if value in (None, ""):
        return None
    try:
        return float(Decimal(str(value).replace(",", ".")))
    except (InvalidOperation, ValueError):
        return None


def bmi_methodology_note(age, imc):
    age_value = parse_float(age)
    imc_value = parse_float(imc)
    if imc_value is None:
        return None
    if age_value is not None and age_value < 20:
        return (
            f"IMC calculado: {imc_value:.2f} kg/m². En menores de 20 años, la clasificación debe "
            "interpretarse con referencias por edad y sexo; compleméntalo con pliegues, masas y somatotipo."
        )
    return (
        "En deportistas, el IMC debe interpretarse junto con masa muscular, grasa corporal y somatotipo, "
        "porque no diferencia masa magra y masa grasa."
    )


def fat_equation_warning(detail, threshold=5.0):
    values = [
        parse_float(detail.get("PorcRasoYuasz")),
        parse_float(detail.get("PorcGrasoFaulker")),
    ]
    values = [value for value in values if value is not None]
    if len(values) < 2:
        return None
    difference = max(values) - min(values)
    if difference < threshold:
        return None
    return (
        f"Diferencia entre ecuaciones: {difference:.2f} %. Interpreta con cautela y usa la misma "
        "ecuación en controles sucesivos para conservar comparabilidad."
    )


def longitudinal_reliability_message(count):
    if count <= 0:
        return "Sin mediciones disponibles para análisis longitudinal."
    if count == 1:
        return "Una medición no permite análisis longitudinal."
    if count == 2:
        return "Comparación entre dos mediciones; se recomiendan al menos tres registros para hablar de tendencia."
    if count < 5:
        return "Tendencia inicial; más mediciones aumentan la confiabilidad del seguimiento."
    return "Tendencia longitudinal con mejor soporte por cantidad de mediciones."
