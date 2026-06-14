from pathlib import Path

from src.frontend.assets import (
    APP_ICON,
    LOGO_CDR,
    LOGO_ISC,
    LOGO_NYQUIST,
    LOGO_SOMATOCARTA,
    LOGO_UTP,
    MODULE_IMAGES,
    REFERENCE_IMAGES,
    WINDOW_ICON,
    asset_path,
)


def test_brand_assets_exist():
    for filename in [LOGO_SOMATOCARTA, LOGO_CDR, LOGO_ISC, LOGO_UTP, LOGO_NYQUIST]:
        assert Path(asset_path(filename)).exists()


def test_flet_launcher_icon_uses_somatocarta_logo():
    logo_path = Path(asset_path(LOGO_SOMATOCARTA))
    icon_path = Path(asset_path(APP_ICON))

    assert icon_path.exists()
    assert icon_path.read_bytes() == logo_path.read_bytes()


def test_windows_window_icon_exists():
    assert Path(asset_path(WINDOW_ICON)).exists()


def test_dashboard_module_images_exist():
    for filename in MODULE_IMAGES.values():
        assert Path(asset_path(filename)).exists()


def test_reference_images_exist():
    for filename in REFERENCE_IMAGES.values():
        assert Path(asset_path(filename)).exists()


def test_main_sets_window_icon_to_somatocarta_logo():
    source = Path("main.py").read_text(encoding="utf-8")

    assert "page.window.icon = asset_path(WINDOW_ICON)" in source
    assert 'ft.app(target=main, assets_dir="assets")' in source


def test_main_blocks_reentrant_login_submits():
    source = Path("main.py").read_text(encoding="utf-8")

    assert "login_in_progress = False" in source
    assert "if login_in_progress:" in source
    assert "login_button_control.disabled = True" in source
