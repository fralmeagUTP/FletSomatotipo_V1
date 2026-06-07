def control_value(control):
    return getattr(control, "value", None)


def required_missing(controls):
    for control, message in controls:
        if not control_value(control):
            return message
    return None


def optional_int(value):
    return int(value) if value else None


def parse_positive_float(value, label: str):
    raw_value = str(value or "").strip()
    if not raw_value:
        raise ValueError(f"{label} es obligatorio")
    parsed_value = float(raw_value.replace(",", "."))
    if parsed_value <= 0:
        raise ValueError(f"{label} debe ser mayor que cero")
    return parsed_value


def parse_positive_float_control(control, label: str):
    return parse_positive_float(control_value(control), label)


def build_deportista_payload(fields: dict, photo_url: str | None):
    return {
        "IDENTI_DEPORTISTA": control_value(fields["identi"]).strip(),
        "TIPO_IDENTI": int(control_value(fields["tipo_identi"]) or 0),
        "NOMBRE_DEPORTISTA": control_value(fields["nombre"]).strip(),
        "SEXO_DEPORTISTA": control_value(fields["sexo"]),
        "FECHA_NAC": control_value(fields["fecha_nac"]) or None,
        "FOTO_DEPORTISTA": photo_url,
        "PAIS_NAC": control_value(fields["pais_nac"]),
        "DEPARTA_NAC": control_value(fields["dep_nac"]),
        "CIUDAD_NAC": control_value(fields["ciudad_nac"]),
        "DEPARTA_RESI": control_value(fields["dep_resi"]),
        "CIUDAD_RESI": control_value(fields["ciudad_resi"]),
        "DIRECC_RESI": control_value(fields["direcc_resi"]),
        "TELEFONO": control_value(fields["telefono"]),
        "E_MAIL": control_value(fields["email"]),
        "ID_ESTRATO": optional_int(control_value(fields["estrato_dd"])),
        "ID_NIVEL": optional_int(control_value(fields["nivel_edu_dd"])),
        "NOMBRE_INSTITU": control_value(fields["nombre_institu"]),
        "OBSERVACIONES": control_value(fields["observaciones"]),
    }


def build_measurement_detail(fields: dict):
    return {
        "ESTA_USER_CM": parse_positive_float_control(fields["estatura"], "Estatura"),
        "PESO_kg": parse_positive_float_control(fields["peso"], "Peso"),
        "PLIEGUE_TRICIPITAL": parse_positive_float_control(fields["p_tricipital"], "Pliegue tricipital"),
        "PLIEGUE_SUBESCAPULAR": parse_positive_float_control(fields["p_subescapular"], "Pliegue subescapular"),
        "PLIEGUE_SUPRAILIACO": parse_positive_float_control(fields["p_suprailiaco"], "Pliegue suprailiaco"),
        "PLIEGUE_ABDOMINAL": parse_positive_float_control(fields["p_abdominal"], "Pliegue abdominal"),
        "PLIEGUE_MUSLO_ANT": parse_positive_float_control(fields["p_muslo"], "Pliegue muslo anterior"),
        "PLIEGUE_MEDIAL_PIERNA": parse_positive_float_control(fields["p_pierna"], "Pliegue pierna medial"),
        "DIAMETRO_BIEPI_MUNECA": parse_positive_float_control(fields["d_muneca"], "Diametro muneca"),
        "DIAMETRO_BIEPI_FEMUR": parse_positive_float_control(fields["d_femur"], "Diametro femur"),
        "DIAMETRO_CODO": parse_positive_float_control(fields["d_codo"], "Diametro codo"),
        "PERIMETRO_BICED_CONTRAIDO": parse_positive_float_control(fields["perim_bicep"], "Perimetro biceps"),
        "PERIMETRO_PIERNA": parse_positive_float_control(fields["perim_pierna"], "Perimetro pierna"),
        "CIRCUNFERENCIA_CARPO": parse_positive_float_control(fields["c_carpo"], "Circunferencia carpo"),
    }


def build_somatotipo_payload(athlete_id: str, login_user: str, fecha_medida: str, observaciones: str, details: list):
    return {
        "IDENTI_DEPORTISTA": athlete_id,
        "LOGIN_USER": login_user,
        "FECHA_MEDIDA": fecha_medida,
        "OBSERV": observaciones,
        "DETALLES": details,
    }
