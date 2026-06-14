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

    def _request_bytes(self, method: str, path: str, include_auth: bool = True, **kwargs):
        timeout = kwargs.pop("timeout", 30)
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
            raise ApiError("El servidor tardÃ³ demasiado en responder.") from error
        except requests.exceptions.ConnectionError as error:
            raise ApiError(
                "No se pudo conectar con el servidor. Verifica que el backend estÃ© encendido."
            ) from error
        if response.status_code >= 400:
            raise ApiError(api_error_message(response), response.status_code)
        return response.content

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

    def get_dashboard_summary(self):
        return self._request("GET", "/dashboard/summary")

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

    def list_entidades_page(self, search: str = "", page: int = 1, page_size: int = 50):
        params = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        return self._request("GET", "/entidades/", params=params)

    def list_entidades(self, search: str = "", page: int = 1, page_size: int = 50):
        return self.list_entidades_page(search, page, page_size)["items"]

    def create_entidad(self, data: dict):
        return self._request("POST", "/entidades/", json=data)

    def update_entidad(self, nit: str, data: dict):
        return self._request("PUT", f"/entidades/{nit}", json=data)

    def delete_entidad(self, nit: str):
        return self._request("DELETE", f"/entidades/{nit}")

    def list_deportes_page(self, search: str = "", page: int = 1, page_size: int = 50):
        params = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        return self._request("GET", "/deportes/", params=params)

    def list_deportes(self, search: str = "", page: int = 1, page_size: int = 50):
        return self.list_deportes_page(search, page, page_size)["items"]

    def create_deporte(self, data: dict):
        return self._request("POST", "/deportes/", json=data)

    def update_deporte(self, deporte_id: int, data: dict):
        return self._request("PUT", f"/deportes/{deporte_id}", json=data)

    def delete_deporte(self, deporte_id: int):
        return self._request("DELETE", f"/deportes/{deporte_id}")

    def list_asignaciones_page(self, search: str = "", page: int = 1, page_size: int = 50):
        params = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        return self._request("GET", "/asignaciones/", params=params)

    def create_asignacion(self, data: dict):
        return self._request("POST", "/asignaciones/", json=data)

    def update_asignacion(self, assignment_id: int, data: dict):
        return self._request("PUT", f"/asignaciones/{assignment_id}", json=data)

    def delete_asignacion(self, assignment_id: int):
        return self._request("DELETE", f"/asignaciones/{assignment_id}")

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

    def list_somatotipos_editables(self, identi: str):
        return self._request("GET", f"/somatotipo/editable/deportista/{identi}")

    def get_somatotipo_editable(self, somatotipo_id: int):
        return self._request("GET", f"/somatotipo/editable/{somatotipo_id}")

    def create_somatotipo_detalle(self, somatotipo_id: int, data: dict):
        return self._request("POST", f"/somatotipo/{somatotipo_id}/detalle", json=data)

    def update_somatotipo_detalle(self, detail_id: int, data: dict):
        return self._request("PUT", f"/somatotipo/detalle/{detail_id}", json=data)

    def delete_somatotipo_detalle(self, detail_id: int):
        return self._request("DELETE", f"/somatotipo/detalle/{detail_id}")

    def get_somatotipo_view_contract(self):
        return self._request("GET", "/somatotipo/vista/contrato")

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

    def get_historial_vista_all(self, identi: str, page_size: int = 100):
        page_size = max(1, min(page_size, 100))
        first_page = self.get_historial_vista_page(identi, 1, page_size)
        items = list(first_page["items"])
        total = int(first_page.get("total") or len(items))
        page = 2
        while len(items) < total:
            page_data = self.get_historial_vista_page(identi, page, page_size)
            page_items = list(page_data.get("items") or [])
            if not page_items:
                break
            items.extend(page_items)
            page += 1
        return items

    def find_deportista_for_historial(self, query: str):
        matches = self.list_deportistas(query)
        if not matches:
            return None
        return matches[0]

    def delete_somatotipo(self, somatotipo_id: int):
        return self._request("DELETE", f"/somatotipo/{somatotipo_id}")

    def download_somatotipo_pdf(self, somatotipo_id: int, output_dir: str | Path | None = None):
        pdf_bytes = self._request_bytes("GET", f"/somatotipo/{somatotipo_id}/pdf")
        if not pdf_bytes.startswith(b"%PDF"):
            raise ApiError("El servidor no devolvió un PDF válido.")
        target_dir = Path(output_dir) if output_dir else Path.home() / "Downloads"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"valoracion_{somatotipo_id}.pdf"
        target_path.write_bytes(pdf_bytes)
        return target_path

    def download_longitudinal_pdf(self, identi: str, output_dir: str | Path | None = None):
        pdf_bytes = self._request_bytes("GET", f"/somatotipo/vista/deportista/{identi}/longitudinal/pdf")
        if not pdf_bytes.startswith(b"%PDF"):
            raise ApiError("El servidor no devolvió un PDF válido.")
        target_dir = Path(output_dir) if output_dir else Path.home() / "Downloads"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"analisis_longitudinal_{identi}.pdf"
        target_path.write_bytes(pdf_bytes)
        return target_path
