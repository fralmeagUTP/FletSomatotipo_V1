from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"

LOGO_SOMATOCARTA = "LogoSomatoCarta.png"
LOGO_CDR = "Logo_CDR_60px.jpg"
LOGO_ISC = "Logo_ISC_60px.jpg"
LOGO_UTP = "Logo_UTP_60px.jpg"
LOGO_NYQUIST = "Logo_Nyquist_60px.jpg"

MODULE_IMAGES = {
    "deportistas": "Deportistas.png",
    "valoracion": "ValoracionCorporal.png",
    "historial": "Historial.png",
    "deportes": "Deportes.png",
    "asignaciones": "Asignaciones.png",
    "entidades": "Entidades.png",
}

REFERENCE_IMAGES = {
    "contextura": "ContexturaFisica.png",
    "imc": "IMC.png",
    "somatocarta": "Somatocarta.png",
    "somatotipos": "Somatotipos.png",
}


def asset_path(filename: str) -> str:
    return str(ASSETS_DIR / filename)
