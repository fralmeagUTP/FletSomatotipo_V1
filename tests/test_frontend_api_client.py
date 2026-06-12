import unittest
import tempfile
from unittest.mock import Mock, patch

import requests

from src.frontend.api_client import ApiClient, ApiError


class FakeSession:
    def __init__(self, token="token-prueba"):
        self.values = {"access_token": token}

    def get(self, key):
        return self.values.get(key)


class FakePage:
    def __init__(self, token="token-prueba"):
        self.session = FakeSession(token)


class ApiClientTests(unittest.TestCase):
    def test_list_deportistas_uses_auth_headers_and_search(self):
        response = Mock(status_code=200, content=b"{}")
        response.json.return_value = {
            "items": [{"IDENTI_DEPORTISTA": "123"}],
            "total": 1,
            "page": 2,
            "page_size": 10,
        }

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).list_deportistas("ana", page=2, page_size=10)

        self.assertEqual(result, [{"IDENTI_DEPORTISTA": "123"}])
        method, url = request.call_args.args
        self.assertEqual(method, "GET")
        self.assertTrue(url.endswith("/deportistas/"))
        self.assertEqual(request.call_args.kwargs["params"], {"search": "ana", "page": 2, "page_size": 10})
        self.assertEqual(
            request.call_args.kwargs["headers"]["Authorization"],
            "Bearer token-prueba",
        )

    def test_list_deportistas_page_wraps_legacy_list_response(self):
        response = Mock(status_code=200, content=b"[]")
        response.json.return_value = [{"IDENTI_DEPORTISTA": "123"}]

        with patch("src.frontend.api_client.requests.request", return_value=response):
            result = ApiClient(FakePage()).list_deportistas_page("ana")

        self.assertEqual(result["items"], [{"IDENTI_DEPORTISTA": "123"}])
        self.assertEqual(result["total"], 1)

    def test_error_response_raises_api_error(self):
        response = Mock(status_code=422, content=b"{}")
        response.json.return_value = {"detail": "Dato invalido"}

        with patch("src.frontend.api_client.requests.request", return_value=response):
            with self.assertRaises(ApiError) as context:
                ApiClient(FakePage()).list_deportistas()

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(str(context.exception), "Dato invalido")

    def test_login_posts_without_auth_header(self):
        response = Mock(status_code=200, content=b"{}")
        response.json.return_value = {"access_token": "abc", "username": "Admin"}

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).login("admin", "secret")

        self.assertEqual(result["access_token"], "abc")
        self.assertEqual(request.call_args.args[0], "POST")
        self.assertTrue(request.call_args.args[1].endswith("/auth/login"))
        self.assertEqual(
            request.call_args.kwargs["json"],
            {"username": "admin", "password": "secret"},
        )
        self.assertNotIn("Authorization", request.call_args.kwargs["headers"])

    def test_connection_error_raises_api_error(self):
        with patch(
            "src.frontend.api_client.requests.request",
            side_effect=requests.exceptions.ConnectionError(),
        ):
            with self.assertRaises(ApiError) as context:
                ApiClient(FakePage()).login("admin", "secret")

        self.assertIn("backend", str(context.exception))

    def test_create_somatotipo_posts_payload(self):
        response = Mock(status_code=200, content=b'{"id": 1}')
        response.json.return_value = {"id": 1}
        payload = {"IDENTI_DEPORTISTA": "123", "DETALLES": []}

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).create_somatotipo(payload)

        self.assertEqual(result, {"id": 1})
        self.assertEqual(request.call_args.args[0], "POST")
        self.assertTrue(request.call_args.args[1].endswith("/somatotipo/"))
        self.assertEqual(request.call_args.kwargs["json"], payload)

    def test_list_somatotipos_editables_uses_athlete_id(self):
        response = Mock(status_code=200, content=b"[]")
        response.json.return_value = [{"id_Somatotipo": 1}]

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).list_somatotipos_editables("123")

        self.assertEqual(result, [{"id_Somatotipo": 1}])
        self.assertEqual(request.call_args.args[0], "GET")
        self.assertTrue(request.call_args.args[1].endswith("/somatotipo/editable/deportista/123"))

    def test_get_somatotipo_editable_uses_somatotipo_id(self):
        response = Mock(status_code=200, content=b"{}")
        response.json.return_value = {"id_Somatotipo": 99}

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).get_somatotipo_editable(99)

        self.assertEqual(result["id_Somatotipo"], 99)
        self.assertEqual(request.call_args.args[0], "GET")
        self.assertTrue(request.call_args.args[1].endswith("/somatotipo/editable/99"))

    def test_update_somatotipo_detalle_puts_payload(self):
        response = Mock(status_code=200, content=b"{}")
        response.json.return_value = {"ID": 7}
        payload = {"PESO_kg": 70}

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).update_somatotipo_detalle(7, payload)

        self.assertEqual(result["ID"], 7)
        self.assertEqual(request.call_args.args[0], "PUT")
        self.assertTrue(request.call_args.args[1].endswith("/somatotipo/detalle/7"))
        self.assertEqual(request.call_args.kwargs["json"], payload)

    def test_create_somatotipo_detalle_posts_payload_to_master(self):
        response = Mock(status_code=200, content=b"{}")
        response.json.return_value = {"ID": 8}
        payload = {"PESO_kg": 71}

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).create_somatotipo_detalle(99, payload)

        self.assertEqual(result["ID"], 8)
        self.assertEqual(request.call_args.args[0], "POST")
        self.assertTrue(request.call_args.args[1].endswith("/somatotipo/99/detalle"))
        self.assertEqual(request.call_args.kwargs["json"], payload)

    def test_delete_somatotipo_detalle_uses_detail_id(self):
        response = Mock(status_code=200, content=b"{}")
        response.json.return_value = {"ID": 8}

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).delete_somatotipo_detalle(8)

        self.assertEqual(result["ID"], 8)
        self.assertEqual(request.call_args.args[0], "DELETE")
        self.assertTrue(request.call_args.args[1].endswith("/somatotipo/detalle/8"))

    def test_get_dashboard_summary_uses_dashboard_endpoint(self):
        response = Mock(status_code=200, content=b"{}")
        response.json.return_value = {"total_deportistas": 2}

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).get_dashboard_summary()

        self.assertEqual(result["total_deportistas"], 2)
        self.assertEqual(request.call_args.args[0], "GET")
        self.assertTrue(request.call_args.args[1].endswith("/dashboard/summary"))

    def test_entidades_client_methods_use_expected_routes(self):
        response = Mock(status_code=200, content=b"{}")
        response.json.return_value = {"items": [{"NIT_ENTIDAD": "900"}], "total": 1, "page": 1, "page_size": 10}

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).list_entidades_page("club", page=1, page_size=10)

        self.assertEqual(result["total"], 1)
        self.assertEqual(request.call_args.args[0], "GET")
        self.assertTrue(request.call_args.args[1].endswith("/entidades/"))
        self.assertEqual(request.call_args.kwargs["params"], {"page": 1, "page_size": 10, "search": "club"})

        payload = {"NIT_ENTIDAD": "900", "RAZON_SOCIAL": "Club"}
        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            ApiClient(FakePage()).update_entidad("900", payload)

        self.assertEqual(request.call_args.args[0], "PUT")
        self.assertTrue(request.call_args.args[1].endswith("/entidades/900"))
        self.assertEqual(request.call_args.kwargs["json"], payload)

    def test_deportes_client_methods_use_expected_routes(self):
        response = Mock(status_code=200, content=b"{}")
        response.json.return_value = {"ID_DEPORTE": 7, "DEPORTE": "Natación"}
        payload = {"DEPORTE": "Natación"}

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).create_deporte(payload)

        self.assertEqual(result["ID_DEPORTE"], 7)
        self.assertEqual(request.call_args.args[0], "POST")
        self.assertTrue(request.call_args.args[1].endswith("/deportes/"))
        self.assertEqual(request.call_args.kwargs["json"], payload)

    def test_asignaciones_client_methods_use_expected_routes(self):
        response = Mock(status_code=200, content=b"{}")
        response.json.return_value = {"id": 1}
        payload = {"ID_DEPORTE": 7, "IDENTI_DEPORTISTA": "123", "NIT_ENTIDAD": "900"}

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).create_asignacion(payload)

        self.assertEqual(result["id"], 1)
        self.assertEqual(request.call_args.args[0], "POST")
        self.assertTrue(request.call_args.args[1].endswith("/asignaciones/"))
        self.assertEqual(request.call_args.kwargs["json"], payload)

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            ApiClient(FakePage()).delete_asignacion(1)

        self.assertEqual(request.call_args.args[0], "DELETE")
        self.assertTrue(request.call_args.args[1].endswith("/asignaciones/1"))

    def test_get_somatotipo_view_contract_uses_contract_endpoint(self):
        response = Mock(status_code=200, content=b"{}")
        response.json.return_value = {"ok": True, "missing": []}

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).get_somatotipo_view_contract()

        self.assertTrue(result["ok"])
        self.assertEqual(request.call_args.args[0], "GET")
        self.assertTrue(request.call_args.args[1].endswith("/somatotipo/vista/contrato"))

    def test_get_historial_uses_deportista_id(self):
        response = Mock(status_code=200, content=b"{}")
        response.json.return_value = {
            "items": [{"id_Somatotipo": 1}],
            "total": 1,
            "page": 2,
            "page_size": 5,
        }

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).get_historial_vista("123", page=2, page_size=5)

        self.assertEqual(result, [{"id_Somatotipo": 1}])
        self.assertEqual(request.call_args.args[0], "GET")
        self.assertTrue(request.call_args.args[1].endswith("/somatotipo/vista/deportista/123"))
        self.assertEqual(request.call_args.kwargs["params"], {"page": 2, "page_size": 5})

    def test_get_historial_vista_page_wraps_legacy_list_response(self):
        response = Mock(status_code=200, content=b"[]")
        response.json.return_value = [{"id_Somatotipo": 1}]

        with patch("src.frontend.api_client.requests.request", return_value=response):
            result = ApiClient(FakePage()).get_historial_vista_page("123")

        self.assertEqual(result["items"], [{"id_Somatotipo": 1}])
        self.assertEqual(result["total"], 1)

    def test_find_deportista_for_historial_returns_first_match(self):
        response = Mock(status_code=200, content=b"[]")
        response.json.return_value = [
            {"IDENTI_DEPORTISTA": "123", "NOMBRE_DEPORTISTA": "Ana"}
        ]

        with patch("src.frontend.api_client.requests.request", return_value=response):
            result = ApiClient(FakePage()).find_deportista_for_historial("ana")

        self.assertEqual(result["IDENTI_DEPORTISTA"], "123")

    def test_find_deportista_for_historial_returns_none_without_matches(self):
        response = Mock(status_code=200, content=b"[]")
        response.json.return_value = []

        with patch("src.frontend.api_client.requests.request", return_value=response):
            result = ApiClient(FakePage()).find_deportista_for_historial("nadie")

        self.assertIsNone(result)

    def test_delete_somatotipo_uses_id(self):
        response = Mock(status_code=200, content=b'{"message": "ok"}')
        response.json.return_value = {"message": "ok"}

        with patch("src.frontend.api_client.requests.request", return_value=response) as request:
            result = ApiClient(FakePage()).delete_somatotipo(99)

        self.assertEqual(result, {"message": "ok"})
        self.assertEqual(request.call_args.args[0], "DELETE")
        self.assertTrue(request.call_args.args[1].endswith("/somatotipo/99"))

    def test_download_somatotipo_pdf_saves_file(self):
        response = Mock(status_code=200, content=b"%PDF-1.4 contenido")

        with tempfile.TemporaryDirectory() as output_dir:
            with patch("src.frontend.api_client.requests.request", return_value=response) as request:
                target_path = ApiClient(FakePage()).download_somatotipo_pdf(99, output_dir)

            self.assertEqual(target_path.name, "valoracion_99.pdf")
            self.assertEqual(target_path.read_bytes(), b"%PDF-1.4 contenido")
            self.assertEqual(request.call_args.args[0], "GET")
            self.assertTrue(request.call_args.args[1].endswith("/somatotipo/99/pdf"))

    def test_download_somatotipo_pdf_rejects_invalid_content(self):
        response = Mock(status_code=200, content=b"no es pdf")

        with tempfile.TemporaryDirectory() as output_dir:
            with patch("src.frontend.api_client.requests.request", return_value=response):
                with self.assertRaises(ApiError) as context:
                    ApiClient(FakePage()).download_somatotipo_pdf(99, output_dir)

        self.assertIn("PDF válido", str(context.exception))

    def test_download_longitudinal_pdf_saves_file(self):
        response = Mock(status_code=200, content=b"%PDF-1.4 longitudinal")

        with tempfile.TemporaryDirectory() as output_dir:
            with patch("src.frontend.api_client.requests.request", return_value=response) as request:
                target_path = ApiClient(FakePage()).download_longitudinal_pdf("123", output_dir)

            self.assertEqual(target_path.name, "analisis_longitudinal_123.pdf")
            self.assertEqual(target_path.read_bytes(), b"%PDF-1.4 longitudinal")
            self.assertEqual(request.call_args.args[0], "GET")
            self.assertTrue(request.call_args.args[1].endswith("/somatotipo/vista/deportista/123/longitudinal/pdf"))


if __name__ == "__main__":
    unittest.main()
