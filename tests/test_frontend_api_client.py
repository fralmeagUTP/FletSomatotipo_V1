import unittest
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


if __name__ == "__main__":
    unittest.main()
