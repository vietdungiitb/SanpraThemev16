"""P2-c noise reduction: hover-reveal row icons + focus/touch fallback.

Test thuan (doc file), chay tren staging host: python3 -m pytest.
Fail-before: hover test do tren base (0 rule); bump test do (base v73).
Lock-tests (casing/guard) xanh tren base theo dinh nghia + mutation rieng.
"""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
DESK_CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "sanpra_uiv16.css"
JS = ROOT / "sanpra_uiv16" / "public" / "js" / "sanpra_uiv16.js"
HOOKS = ROOT / "sanpra_uiv16" / "hooks.py"


def rule_bodies(css, needle):
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


class NoiseReductionP2cTest(unittest.TestCase):
    def test_hover_icons_hidden_by_default(self):
        css = DESK_CSS.read_text(encoding="utf-8")
        bodies = rule_bodies(css, ".list-row-activity")
        bodies += rule_bodies(css, ".list-row-like")
        self.assertTrue(bodies, "mat rule .list-row-activity/.list-row-like")
        combined = "\n".join(bodies)
        self.assertIn("opacity: 0", combined)
        self.assertIn(".list-row:hover", css)
        self.assertIn(":focus-within", css)
        self.assertIn(".list-row-container:focus-within", css)
        self.assertIn("hover: none", css)

    def test_header_casing_single_rule(self):
        """Khoa nhat quan: dung 1 rule text-transform cho list header."""
        css = DESK_CSS.read_text(encoding="utf-8")
        bodies = rule_bodies(css, ".list-row-head")
        count = sum(1 for b in bodies if "text-transform" in b)
        self.assertEqual(count, 1)

    def test_setup_guide_auto_dismiss_kept(self):
        """Khoa logic tu-an: khong duoc go block auto-dismiss."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn("st_setup_", js)
        self.assertIn("Auto-dismiss once everything is configured", js)

    def test_p2c_bump_v(self):
        hooks = HOOKS.read_text(encoding="utf-8")
        self.assertIn("sanpra_uiv16.css?v=74", hooks)


if __name__ == "__main__":
    unittest.main()
