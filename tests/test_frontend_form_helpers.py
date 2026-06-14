import unittest
from types import SimpleNamespace

from src.frontend.form_helpers import (
    build_deportista_payload,
    build_measurement_detail,
    build_somatotipo_payload,
    parse_positive_float,
    required_missing,
)


def control(value):
    return SimpleNamespace(value=value)


class FormHelpersTests(unittest.TestCase):
    def test_required_missing_returns_first_missing_message(self):
        message = required_missing(
            [
                (control("123"), "ID requerido"),
                (control(""), "Nombre requerido"),
                (control("M"), "Sexo requerido"),
            ]
        )

        self.assertEqual(message, "Nombre requerido")

    def test_required_missing_returns_none_when_valid(self):
        self.assertIsNone(required_missing([(control("123"), "ID requerido")]))

    def test_parse_positive_float_accepts_comma_decimal(self):
        self.assertEqual(parse_positive_float("72,5", "Peso"), 72.5)

    def test_parse_positive_float_rejects_zero(self):
        with self.assertRaises(ValueError):
            parse_positive_float("0", "Peso")

    def test_build_deportista_payload_normalizes_types(self):
        fields = {
            "identi": control(" 123 "),
            "tipo_identi": control("1"),
            "nombre": control(" Ana "),
            "sexo": control("F"),
            "fecha_nac": control("2000-01-01"),
            "pais_nac": control("Colombia"),
            "dep_nac": control("Antioquia"),
            "ciudad_nac": control("Medellín"),
            "dep_resi": control("Antioquia"),
            "ciudad_resi": control("Medellín"),
            "direcc_resi": control("Calle 1"),
            "telefono": control("300"),
            "email": control("ana@test.com"),
            "estrato_dd": control("3"),
            "nivel_edu_dd": control("2"),
            "nombre_institu": control("Club"),
            "observaciones": control("Obs"),
        }

        payload = build_deportista_payload(fields, "foto.png")

        self.assertEqual(payload["IDENTI_DEPORTISTA"], "123")
        self.assertEqual(payload["TIPO_IDENTI"], 1)
        self.assertEqual(payload["ID_ESTRATO"], 3)
        self.assertEqual(payload["FOTO_DEPORTISTA"], "foto.png")

    def test_build_measurement_detail_maps_all_fields(self):
        fields = {
            "estatura": control("180"),
            "peso": control("75"),
            "p_tricipital": control("10"),
            "p_subescapular": control("11"),
            "p_suprailiaco": control("12"),
            "p_abdominal": control("13"),
            "p_muslo": control("14"),
            "p_pierna": control("15"),
            "d_muneca": control("6"),
            "d_femur": control("9"),
            "d_codo": control("7"),
            "perim_bicep": control("32"),
            "perim_pierna": control("40"),
            "c_carpo": control("17"),
        }

        detail = build_measurement_detail(fields)

        self.assertEqual(detail["ESTA_USER_CM"], 180)
        self.assertEqual(detail["PESO_kg"], 75)
        self.assertEqual(detail["CIRCUNFERENCIA_CARPO"], 17)

    def test_build_measurement_detail_rejects_out_of_range_values(self):
        fields = {
            "estatura": control("251"),
            "peso": control("75"),
            "p_tricipital": control("10"),
            "p_subescapular": control("11"),
            "p_suprailiaco": control("12"),
            "p_abdominal": control("13"),
            "p_muslo": control("14"),
            "p_pierna": control("15"),
            "d_muneca": control("6"),
            "d_femur": control("9"),
            "d_codo": control("7"),
            "perim_bicep": control("32"),
            "perim_pierna": control("40"),
            "c_carpo": control("17"),
        }

        with self.assertRaises(ValueError):
            build_measurement_detail(fields)

    def test_build_somatotipo_payload_groups_header_and_details(self):
        payload = build_somatotipo_payload("123", "admin", "2026-06-06", "Obs", [{"PESO_kg": 75}])

        self.assertEqual(payload["IDENTI_DEPORTISTA"], "123")
        self.assertEqual(payload["LOGIN_USER"], "admin")
        self.assertEqual(payload["DETALLES"], [{"PESO_kg": 75}])


if __name__ == "__main__":
    unittest.main()
