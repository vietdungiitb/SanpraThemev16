"""P1-1 touch-target bundle: toolbar buttons/checkboxes/filter inputs >= 36px.

Test thuan (doc file), chay tren staging host: python3 -m pytest.
Fail-before: moi assert deu do tren base @658d0b1 (st-tb-qn-btn 30px,
app-switcher 26px, notif btn 30px, options-close 28px, filter 28px,
checkbox 14px). Mutation: xoá declaration moi -> do lai.
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


def min_px(body, prop):
    """Tra ve so px nho nhat trong declaration `prop: Npx` cua body."""
    vals = []
    for m in re.finditer(r"%s:\s*(\d+)px" % re.escape(prop), body):
        vals.append(int(m.group(1)))
    return min(vals) if vals else None


class TouchTargetP11Test(unittest.TestCase):
    def test_st_tb_qn_btn_at_least_36(self):
        css = DESK_CSS.read_text(encoding="utf-8")
        bodies = rule_bodies(css, ".st-tb-qn-btn {")
        self.assertTrue(bodies, "mat block .st-tb-qn-btn")
        b = bodies[0]
        self.assertGreaterEqual(min_px(b, "width"), 36)
        self.assertGreaterEqual(min_px(b, "height"), 36)

    def test_st_tb_app_switcher_at_least_36(self):
        css = DESK_CSS.read_text(encoding="utf-8")
        # block co border: 1px solid rgba(255,255,255,0.18) sau width/height
        bodies = rule_bodies(css, "#st-top-toolbar #st-tb-app-switcher {")
        self.assertTrue(bodies, "mat block #st-tb-app-switcher")
        b = bodies[0]
        self.assertGreaterEqual(min_px(b, "width"), 36)
        self.assertGreaterEqual(min_px(b, "height"), 36)

    def test_notif_btn_at_least_36(self):
        css = DESK_CSS.read_text(encoding="utf-8")
        bodies = rule_bodies(css, ".desktop-notifications .btn-reset,")
        self.assertTrue(bodies, "mat block notif btn-reset")
        b = bodies[0]
        self.assertGreaterEqual(min_px(b, "width"), 36)
        self.assertGreaterEqual(min_px(b, "height"), 36)

    def test_options_panel_close_at_least_36(self):
        css = DESK_CSS.read_text(encoding="utf-8")
        bodies = rule_bodies(css, "#st-options-panel-close {")
        self.assertTrue(bodies, "mat block #st-options-panel-close")
        b = bodies[0]
        self.assertGreaterEqual(min_px(b, "width"), 36)
        self.assertGreaterEqual(min_px(b, "height"), 36)

    def test_filter_inputs_min_height_36(self):
        css = DESK_CSS.read_text(encoding="utf-8")
        self.assertIn(".standard-filter-section input.form-control.input-xs", css)
        self.assertIn("min-height: 36px !important", css)

    def test_checkbox_min_18(self):
        css = DESK_CSS.read_text(encoding="utf-8")
        self.assertIn("width: 18px !important", css)
        self.assertIn("height: 18px !important", css)

    def test_p1_1_bump_v(self):
        hooks = HOOKS.read_text(encoding="utf-8")
        self.assertIn("sanpra_uiv16.css?v=72", hooks)


if __name__ == "__main__":
    unittest.main()
