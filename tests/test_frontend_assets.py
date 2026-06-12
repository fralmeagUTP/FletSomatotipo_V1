from pathlib import Path

from src.frontend.assets import (
    LOGO_CDR,
    LOGO_ISC,
    LOGO_NYQUIST,
    LOGO_SOMATOCARTA,
    LOGO_UTP,
    MODULE_IMAGES,
    REFERENCE_IMAGES,
    asset_path,
)


def test_brand_assets_exist():
    for filename in [LOGO_SOMATOCARTA, LOGO_CDR, LOGO_ISC, LOGO_UTP, LOGO_NYQUIST]:
        assert Path(asset_path(filename)).exists()


def test_dashboard_module_images_exist():
    for filename in MODULE_IMAGES.values():
        assert Path(asset_path(filename)).exists()


def test_reference_images_exist():
    for filename in REFERENCE_IMAGES.values():
        assert Path(asset_path(filename)).exists()
