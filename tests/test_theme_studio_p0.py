"""Theme Studio P0 — font TV + toolbar scroll + semantic heading.

Guard cho 3 loi P0 trong AUDIT_THEME_STUDIO_UI_20261109.md:
F1 heading serif Georgia vo dau TV; F2 toolbar 1 hang 55px khong scroll
nen nut wrap 2-3 dong khi nhan VI dai; F3 thieu header tag (div thay h3/header/nav).

Lesson 61: assert tren gia tri (selector co rule), khong tren ten ham.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIO_CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "theme_studio.css"
STUDIO_JS = (
    ROOT / "sanpra_uiv16" / "sanpra_ui_v16" / "page" / "theme_studio" / "theme_studio.js"
)

# Chi 3 selector heading duoc phep bo Georgia; logo/metric trang tri giu nguyen.
HEADING_SELECTORS = (".sts-controls h2", ".sts-preview-heading h3", ".sts-inspector-head b")


def _rule_block(css, selector):
    start = css.find(selector)
    if start == -1:
        return None
    brace_open = css.find("{", start)
    brace_close = css.find("}", brace_open)
    if brace_open == -1 or brace_close == -1:
        return None
    return css[brace_open + 1 : brace_close]


class StudioHeadingFontTest(unittest.TestCase):
    def test_heading_khong_dung_georgia(self):
        """Fail-before: 3/3 heading con Georgia. Sau fix: 0/3."""
        css = STUDIO_CSS.read_text(encoding="utf-8")
        bad = [
            sel
            for sel in HEADING_SELECTORS
            if (_rule_block(css, sel) or "").find("Georgia") != -1
        ]
        self.assertEqual(bad, [], "heading van dung Georgia (vo dau TV): %r" % (bad,))


class StudioToolbarScrollTest(unittest.TestCase):
    def test_toolbar_co_scroll_ngang(self):
        """Fail-before: .sts-toolbar khong overflow-x. Sau fix: co."""
        css = STUDIO_CSS.read_text(encoding="utf-8")
        block = _rule_block(css, ".sts-toolbar") or ""
        compact = re.sub(r"\s+", "", block)
        self.assertIn("overflow-x:auto", compact, "toolbar thieu overflow-x:auto")

    def test_scene_switch_khong_bi_ep_co(self):
        css = STUDIO_CSS.read_text(encoding="utf-8")
        block = _rule_block(css, ".sts-scene-switch") or ""
        compact = re.sub(r"\s+", "", block)
        self.assertIn("flex:00auto", compact, "scene-switch thieu flex:0 0 auto")


class StudioHeadingOrderTest(unittest.TestCase):
    def test_section_title_dung_h3_va_toolbar_dung_header(self):
        """Fail-before: render dung div.sts-section-title + div.sts-toolbar. Sau fix: h3/header."""
        js = STUDIO_JS.read_text(encoding="utf-8")
        self.assertNotIn(
            '<div class="sts-section-title">',
            js,
            "section-title van la div (thieu h3)",
        )
        self.assertNotIn(
            "'<div class=\"sts-toolbar\">'",
            js,
            "toolbar van la div (thieu header)",
        )
        self.assertIn("<h3", js, "thieu h3 trong render")
        self.assertIn("<header", js, "thieu header trong render")


if __name__ == "__main__":
    unittest.main()
