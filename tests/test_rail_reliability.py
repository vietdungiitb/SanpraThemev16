"""Rail tin cay: retry page-change + warn + debug + single-source header (T2/T3/T4).

Co che gan rail giu nguyen (container-level, `$container.before`) + thu tu 8 icon
giu nguyen theo cac phien truoc — file nay chi khoa hanh vi moi, khong doi cu.
Test thuan (doc file), chay tren staging host: python3 -m pytest.
"""

import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "sanpra_uiv16" / "public" / "js" / "sanpra_uiv16.js"
SIDEBAR_CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "sidebar.css"
DESK_CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "sanpra_uiv16.css"
PALETTE_CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "command_palette.css"


def page_change_block(js):
    """Khoi dang ky page-change chua injectIconRail (noi race an)."""
    i = js.find('on("page-change"')
    if i == -1:
        return ""
    return js[i:i + 1200]


class RailRetryTest(unittest.TestCase):
    def test_page_change_cho_container_chu_khong_return_ngay(self):
        """Fail-before T2: page-change phai doi container (retry), khong check 1 lan."""
        block = page_change_block(JS.read_text(encoding="utf-8"))
        self.assertTrue(block, "khong tim thay dang ky page-change")
        self.assertTrue(
            ("sidebarReady" in block) or ("requestAnimationFrame" in block)
            or ("railContainerReady" in block),
            "page-change van one-shot: container render cham la mat rail",
        )

    def test_rail_warn_khi_bo_cuoc(self):
        """Fail-before T2: bo cuoc phai co warn kem reason, khong im lang."""
        js = JS.read_text(encoding="utf-8")
        self.assertTrue(
            ("console.warn('[st-rail" in js) or ('console.warn("[st-rail' in js),
            "thieu warn [st-rail] khi bo cuoc",
        )

    def test_rail_debug_hook_ton_tai(self):
        """Fail-before T2: phai co window.stRailDebug() de bao cao 1 dong."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn("stRailDebug", js)


class HeaderOffsetTest(unittest.TestCase):
    def test_toolbar_height_single_source(self):
        """Fail-before T3: block #st-top-toolbar khong con height px cung."""
        css = DESK_CSS.read_text(encoding="utf-8")
        blocks = []
        start = 0
        while True:
            i = css.find("#st-top-toolbar {", start)
            if i == -1:
                break
            end = css.find("}", i)
            blocks.append(css[i:end] if end != -1 else css[i:i + 800])
            start = i + 1
        self.assertTrue(blocks, "mat block #st-top-toolbar")
        mains = [b for b in blocks if "z-index" in b]
        self.assertTrue(mains, "mat block toolbar chinh")
        block = mains[0]
        self.assertIsNone(
            re.search(r"height:\s*\d+px", block),
            "toolbar van height cung trong khi engine sinh var",
        )
        self.assertIn("var(--st-header-height", block)

    def test_search_modal_ne_toolbar(self):
        """Fail-before T3: modal search goc phai co override ne toolbar."""
        css = (PALETTE_CSS.read_text(encoding="utf-8")
               + DESK_CSS.read_text(encoding="utf-8"))
        self.assertIn("navbar-modal-wrapper", css)
        i = css.find("navbar-modal-wrapper")
        self.assertIn("margin-top", css[max(0, i - 400):i + 400])


class RailSwitchLockTest(unittest.TestCase):
    def test_click_rail_dung_set_route(self):
        """Khoa T4: click rail di SPA set_route, khong qua desk (da xanh tu truoc)."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn("frappe.set_route(route)", js)


if __name__ == "__main__":
    unittest.main()


class AssetVersionTest(unittest.TestCase):
    def test_asset_doi_phai_bump_v(self):
        """Fail-before: doi asset ma quen bump ?v= la trinh duyet giu JS/CSS cu.
        Quy uoc hooks.py: Query versions are bumped whenever an asset changes."""
        hooks = (ROOT / "sanpra_uiv16" / "hooks.py").read_text(encoding="utf-8")
        self.assertIn("sanpra_uiv16.js?v=73", hooks)
        self.assertIn("sanpra_uiv16.css?v=75", hooks)
        self.assertIn("command_palette.css?v=6", hooks)
