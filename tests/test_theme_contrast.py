"""Static contrast guard for the theme's default accent (T002/T202).

The default accent must be #B35200 (not the legacy #F57C00) and must reach
WCAG AA (>= 4.5:1) against white. This test is intentionally RED against
the old default so a regression back to #F57C00 is caught before deploy.
"""

import importlib.util
import sys
import re
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = ROOT / "sanpra_uiv16" / "theme_engine.py"

ACCENT_KEYS = ("accent_color", "sidebar_active_color", "primary_button_color",
               "focus_color", "checkbox_color")
REQUIRED_ACCENT = "#B35200"
LEGACY_ACCENT = "#F57C00"
MIN_CONTRAST = 4.5


class FrappeStub(types.ModuleType):
    def throw(self, message):
        raise ValueError(message)


def load_engine():
    previous = sys.modules.get("frappe")
    sys.modules["frappe"] = FrappeStub("frappe")
    try:
        spec = importlib.util.spec_from_file_location("theme_contrast_module", ENGINE_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if previous is None:
            del sys.modules["frappe"]
        else:
            sys.modules["frappe"] = previous


def test_default_accent_is_b35200():
    engine = load_engine()
    cfg = engine.DEFAULT_CONFIG
    for key in ACCENT_KEYS:
        assert cfg[key] == REQUIRED_ACCENT, (
            f"DEFAULT_CONFIG[{key!r}] = {cfg[key]!r}, expected {REQUIRED_ACCENT!r} "
            f"(legacy {LEGACY_ACCENT!r} must not be the default)"
        )


def test_default_accent_contrast_against_white():
    engine = load_engine()
    cfg = engine.DEFAULT_CONFIG
    for key in ACCENT_KEYS:
        ratio = engine.contrast_ratio(cfg[key], "#FFFFFF")
        assert ratio >= MIN_CONTRAST, (
            f"DEFAULT_CONFIG[{key!r}] = {cfg[key]!r} has contrast {ratio:.2f}:1 "
            f"against white, below WCAG AA {MIN_CONTRAST}:1"
        )


CSS_DIR = ROOT / "sanpra_uiv16" / "public" / "css"
FALLBACK_RE = re.compile(r"var\(\s*--st-accent\s*,\s*#f57c00\s*\)", re.I)


def test_no_accent_fallback_in_css():
    hits = []
    for pth in CSS_DIR.glob("*.css"):
        for i, line in enumerate(pth.read_text(encoding="utf-8").splitlines(), 1):
            if FALLBACK_RE.search(line):
                hits.append(f"{pth.name}:{i}")
    assert not hits, f"con fallback accent: {hits}"


def test_login_css_no_override_cam():
    text = (CSS_DIR / "login.css").read_text(encoding="utf-8")
    assert not re.search(r"--st-accent\s*:\s*#F57C00", text, re.I)


def test_boot_py_no_fallback_cam():
    text = (ROOT / "sanpra_uiv16" / "boot.py").read_text(encoding="utf-8")
    assert 'bootinfo.st_accent = "#F57C00"' not in text
