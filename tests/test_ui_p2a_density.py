"""P2-a density list: row height 32-36px + sticky header + zebra.

Test thuan (doc file), chay tren staging host: python3 -m pytest.
Fail-before: moi assert deu do tren base (padding 10px, khong sticky, khong zebra).
"""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
DESK_CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "sanpra_uiv16.css"
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


class DensityListP2aTest(unittest.TestCase):
    def test_list_row_padding_compact(self):
        css = DESK_CSS.read_text(encoding="utf-8")
        bodies = rule_bodies(css, ".list-row {")
        self.assertTrue(bodies, "mat block .list-row")
        b = bodies[0]
        # padding shorthand phai <= 8px vertical
        import re
        m = re.search(r"padding:\s*(\d+)px", b)
        self.assertIsNotNone(m, "mat declaration padding")
        self.assertLessEqual(int(m.group(1)), 8)

    def test_list_row_min_height(self):
        css = DESK_CSS.read_text(encoding="utf-8")
        bodies = rule_bodies(css, ".list-row {")
        b = bodies[0]
        self.assertIn("min-height", b)
        m = re.search(r"min-height:\s*(\d+)px", b)
        self.assertIsNotNone(m)
        self.assertLessEqual(int(m.group(1)), 36)
        self.assertGreaterEqual(int(m.group(1)), 32)

    def test_list_header_sticky(self):
        css = DESK_CSS.read_text(encoding="utf-8")
        self.assertIn("position: sticky", css)
        self.assertIn("top: var(--st-header-height", css)

    def test_list_zebra_stripe(self):
        css = DESK_CSS.read_text(encoding="utf-8")
        self.assertIn("nth-child(even)", css)

    def test_p2a_bump_v(self):
        hooks = HOOKS.read_text(encoding="utf-8")
        self.assertIn("sanpra_uiv16.css?v=75", hooks)


if __name__ == "__main__":
    unittest.main()
