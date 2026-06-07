from pathlib import Path

import requests

from app_config import API_URL, api_error_message, auth_headers


class ApiError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    def __init__(self, page, base_url: str = API_URL):
        self.page = page
        self.base_url = base_url

    def _request(self, method: str, path: str, include_auth: bool = True, **kwargs):
        timeout = kwargs.pop("timeout", 15)
        headers = kwargs.pop("headers", {})
        if include_auth:
            headers.update(auth_headers(self.page))
        try:
            response = requests.request(
                method,
                f"{self.base_url}{path}",
                headers=headers,
                timeout=timeout,
                **kwargs,
            )
        except requests.exceptions.Timeout as error:
            raise ApiError("El servidor tardó demasiado en responder.") from error
        except requests.exceptions.ConnectionError as error:
            raise ApiError(
                "No se pudo conectar con el servidor. Verifica que el backend esté encendido."
            ) from error
        if response.status_code >= 400:
            raise ApiError(api_error_message(response), response.status_code)
        if not response.content:
            return None
        return response.json()

    def login(self, username: str, password: str):
        return self._request(
            "POST",
            "/auth/login",
            include_auth=False,
            json={"username": username, "password": password},
        )

    def get_catalogs(self):
        return {
            "tipos_documentos": self._request("GET", "/catalogos/tipos_documento"),
            "estratos": self._request("GET", "/catalogos/estratos"),
            "niveles_educativos": self._request("GET", "/catalogos/niveles_educativos"),
        }

    def list_deportistas_page(self, search: str = "", page: int = 1, page_size: int = 50):
        params = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        result = self._request("GET", "/deportistas/", params=params)
        if isinstance(result, list):
            return {"items": result, "total": len(result), "page": page, "page_size": page_size}
        return result

    def list_deportistas(self, search: str = "", page: int = 1, page_size: int = 50):
        return self.list_deportistas_page(search, page, page_size)["items"]

    def create_deportista(self, data: dict):
        return self._request("POST", "/deportistas/", json=data)

    def update_deportista(self, identi: str, data: dict):
        return self._request("PUT", f"/deportistas/{identi}", json=data)

    def delete_deportista(self, identi: str):
        return self._request("DELETE", f"/deportistas/{identi}")

    def upload_photo(self, file_path: str):
        path = Path(file_path)
        with path.open("rb") as file:
            result = self._request(
                "POST",
                "/files/upload",
                files={"file": (path.name, file)},
                timeout=30,
            )
        return f"{self.base_url}{result['url']}"

    def create_somatotipo(self, data: dict):
        return self._request("POST", "/somatotipo/", json=data)

    def get_historial_vista_page(self, identi: str, page: int = 1, page_size: int = 20):
        result = self._request(
            "GET",
            f"/somatotipo/vista/deportista/{identi}",
            params={"page": page, "page_size": page_size},
        )
        if isinstance(result, list):
            return {"items": result, "total": len(result), "page": page, "page_size": page_size}
        return result

    def get_historial_vista(self, identi: str, page: int = 1, page_size: int = 20):
        return self.get_historial_vista_page(identi, page, page_size)["items"]

    def find_deportista_for_historial(self, query: str):
        matches = self.list_deportistas(query)
        if not matches:
            return None
        return matches[0]

    def delete_somatotipo(self, somatotipo_id: int):
        return self._request("DELETE", f"/somatotipo/{somatotipo_id}")
