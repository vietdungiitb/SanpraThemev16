"""UI-P0: phan cap sidebar cha/con + gutters content can bang.

Test thuan (doc file), chay tren staging host: python3 -m pytest.
- REQ-01: muc .indent (con) phai khac muc cha bang mat: padding-left + font-size
  rieng. Cam assert rong kieu assertIn("padding", ...) vi shorthand
  `padding: 2px 4px` da ton tai tu base -> xanh gia (lesson 61).
- REQ-02: .page-container desktop phai co gutters trai/phai >= 24px, scoped
  min-width:769px de khong de rule mobile 12px (max-width:768px).
- REQ-04: hooks.py bump ?v= sidebar 39->40, sanpra 68->69 (lesson 75).
"""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SIDEBAR_CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "sidebar.css"
DESK_CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "sanpra_uiv16.css"
HOOKS = ROOT / "sanpra_uiv16" / "hooks.py"


def rule_bodies(css, needle):
    """Tra ve list body (trong {...}) cua cac rule ma selector chua needle.

    Trich bang dem dau ngoac (lesson 64), khong cat chuoi tho so theo do dai
    co dinh de tranh mat declaration o cuoi block.
    """
    out = []
    i = 0
    n = len(css)
    while True:
        j = css.find(needle, i)
        if j == -1:
            break
        k = css.find("{", j)
        if k == -1:
            break
        depth = 0
        m = k
        while m < n:
            if css[m] == "{":
                depth += 1
            elif css[m] == "}":
                depth -= 1
                if depth == 0:
                    break
            m += 1
        out.append(css[k:m + 1] if m < n else css[k:k + 800])
        i = k + 1
    return out


class SidebarHierarchyTest(unittest.TestCase):
    def test_indent_co_visual_differentiation(self):
        """Fail-before REQ-01: block .indent phai co padding-left + font-size
        rieng, khong the dung chung declarations voi muc cha."""
        css = SIDEBAR_CSS.read_text(encoding="utf-8")
        bodies = rule_bodies(css, ".standard-sidebar-item.indent")
        self.assertTrue(bodies, "mat block .standard-sidebar-item.indent")
        combined = "\n".join(bodies)
        self.assertIn("padding-left", combined)
        self.assertIn("24px", combined)
        self.assertIn("font-size", combined)
        self.assertIn("13px", combined)

    def test_indent_giu_active_doc_duoc(self):
        """Muc con dang active van doc duoc: phai co carve-out active."""
        css = SIDEBAR_CSS.read_text(encoding="utf-8")
        bodies = rule_bodies(css, ".standard-sidebar-item.indent.active-sidebar")
        self.assertTrue(bodies, "mat carve-out .indent.active-sidebar")


class ContentGuttersTest(unittest.TestCase):
    def test_page_container_co_gutters_desktop(self):
        """Fail-before REQ-02: .page-container desktop co gutters 24px,
        scoped min-width:769px de giu mobile 12px."""
        css = DESK_CSS.read_text(encoding="utf-8")
        self.assertIn("min-width: 769px", css)
        bodies = rule_bodies(css, "body.st-has-toolbar .page-container")
        with_gutters = [b for b in bodies
                        if "padding-left" in b and "padding-right" in b]
        self.assertTrue(with_gutters, "mat rule gutters desktop")
        combined = "\n".join(with_gutters)
        self.assertIn("24px", combined)


class P0AssetVersionTest(unittest.TestCase):
    def test_p0_bump_v(self):
        """Fail-before REQ-04: doi 2 file CSS phai bump ?v= cung commit."""
        hooks = HOOKS.read_text(encoding="utf-8")
        self.assertIn("sidebar.css?v=41", hooks)
        self.assertIn("sanpra_uiv16.css?v=75", hooks)


if __name__ == "__main__":
    unittest.main()
