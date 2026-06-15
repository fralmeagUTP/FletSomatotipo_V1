import unittest
from datetime import date
from types import SimpleNamespace

from src.backend.services.pdf_service import build_longitudinal_pdf, build_valoracion_pdf, display_value, short_text, value_with_unit


class PdfServiceTests(unittest.TestCase):
    def test_display_value_formats_dates_and_empty_values(self):
        self.assertEqual(display_value(None), "---")
        self.assertEqual(display_value(date(2026, 6, 6)), "2026-06-06")

    def test_short_text_summarizes_long_scale_descriptions(self):
        value = "MODERADO: Moderada adiposidad relativa, la grasa subcutánea cubre contornos"

        self.assertEqual(short_text(value), "MODERADO")

    def test_value_with_unit_appends_measurement_unit(self):
        record = SimpleNamespace(PESO_kg=73)

        self.assertEqual(value_with_unit(record, "PESO_kg", "kg"), "73 kg")

    def test_build_valoracion_pdf_returns_pdf_bytes(self):
        record = SimpleNamespace(
            id_Somatotipo=1,
            NOMBRE_DEPORTISTA="Ana Perez",
            IDENTI_DEPORTISTA="123",
            FECHA_MEDIDA=date(2026, 6, 6),
            EDAD=20,
            SEXO_DEPORTISTA="F",
            PESO_kg=65,
            ESTA_USER_CM=170,
            IMC=22.5,
            EstadoIMC="Normal",
            TipoComplexion="Media",
            Complexion=10.2,
            DIAMETRO_BIEPI_MUNECA=55,
            DIAMETRO_BIEPI_FEMUR=92,
            DIAMETRO_CODO=68,
            PorcGrasoJonson=22.0,
            PesoGrasoJhonston=14.3,
            PesoOseo=8.1,
            PesoResidual=12.8,
            Mma=29.8,
            Endomorfismo=3.1,
            EscalaEndomorfismo="Moderado",
            Mesomorfismo=4.2,
            EscalaMesomorfismo="Alto",
            Ectomorfismo=2.0,
            EscalaEctomorfismo="Bajo",
            X=1.1,
            Y=8.2,
        )

        pdf = build_valoracion_pdf(record)

        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertIn(b"Resultados de valoraci", pdf)
        self.assertIn(b"Unidad", pdf)
        self.assertIn(b"mm", pdf)
        self.assertIn(b"kg", pdf)
        self.assertIn(b"/Count 3", pdf)
        self.assertIn(b"Datos crudos antropom", pdf)
        self.assertIn(b"5.50", pdf)
        self.assertIn(b"M", pdf)
        self.assertIn(b"todo principal: Johnston", pdf)
        self.assertIn(b"Sem", pdf)
        self.assertIn(b"Distribuci", pdf)
        self.assertNotIn(b"Notas de lectura", pdf)
        self.assertNotIn(b"Lectura de coordenadas", pdf)
        self.assertIn(b"/XObject", pdf)
        self.assertIn(b"/ImLogo", pdf)
        self.assertIn(b"/ImContextura", pdf)
        self.assertIn(b"/ImSomatocarta", pdf)
        self.assertIn(b"/ImIMC", pdf)
        self.assertTrue(pdf.endswith(b"%%EOF"))

    def test_build_longitudinal_pdf_returns_pdf_with_somatocarta(self):
        records = [
            SimpleNamespace(
                id_Somatotipo=1,
                NOMBRE_DEPORTISTA="Ana Perez",
                IDENTI_DEPORTISTA="123",
                FECHA_MEDIDA=date(2026, 6, 1),
                PESO_kg=65,
                IMC=22.5,
                PorcGrasoJonson=14.9,
                PorcGrasoFaulker=15.4,
                PorcRasoYuasz=15.1,
                Mma=28.3,
                Endomorfismo=3.1,
                Mesomorfismo=4.2,
                Ectomorfismo=2.0,
                X=-0.28,
                Y=9.15,
            ),
            SimpleNamespace(
                id_Somatotipo=2,
                NOMBRE_DEPORTISTA="Ana Perez",
                IDENTI_DEPORTISTA="123",
                FECHA_MEDIDA=date(2026, 6, 15),
                PESO_kg=66,
                IMC=22.8,
                PorcGrasoJonson=14.4,
                PorcGrasoFaulker=15.0,
                PorcRasoYuasz=14.8,
                Mma=29.0,
                Endomorfismo=2.9,
                Mesomorfismo=4.6,
                Ectomorfismo=2.1,
                X=-0.47,
                Y=8.93,
            ),
        ]

        pdf = build_longitudinal_pdf(records)

        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertIn(b"Informe de an", pdf)
        self.assertIn(b"/Count 3", pdf)
        self.assertIn(b"Dashboard de tendencias", pdf)
        self.assertIn(b"Peso vs masa muscular", pdf)
        self.assertIn(b"Grasa: Johnston", pdf)
        self.assertIn(b"Faulkner", pdf)
        self.assertIn(b"Yuhasz", pdf)
        self.assertIn(b"Historial de coordenadas", pdf)
        self.assertIn(b"/ImLogo", pdf)
        self.assertIn(b"/ImSomatocarta", pdf)
        self.assertIn(b"2026-06-15", pdf)
        self.assertTrue(pdf.endswith(b"%%EOF"))


if __name__ == "__main__":
    unittest.main()
