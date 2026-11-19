"""Static guards over the shipped desktop half (catalog-style checks)."""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
JS = (REPO / "desktop" / "plugin.js").read_text()


def test_build_stamp_matches_manifest_version():
    import yaml
    version = yaml.safe_load((REPO / "plugin.yaml").read_text())["version"]
    assert f"const BUILD = '{version}" in JS


def test_id_matches_folder_and_route():
    assert "id: 'tvl-studio'" in JS
    assert "path: '/tvl-studio'" in JS


def test_no_page_reload_and_no_raw_fetch():
    assert "window.location.reload()" not in JS
    assert "fetch(" not in JS  # backend access only via ctx.rest


def test_no_invalid_tailwind_hex_shorthand():
    assert "text-(#" not in JS and "bg-(#" not in JS


def test_tvl_branding_is_on_the_app():
    assert "#0a0e1a" in JS  # TVL canvas
    assert "#22d3ee" in JS  # TVL cyan
    assert "#8b5cf6" in JS  # TVL violet
    assert "TVL STUDIO" in JS


def test_agent_handoff_uses_the_composer_door():
    assert "host.composer.submit(" in JS


def test_brand_dropdown_is_live_not_dead():
    assert "disabled: true" not in JS
    assert "/brand" in JS
