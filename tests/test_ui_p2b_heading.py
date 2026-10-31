"""P2-b H1 semantics: page title gets role=heading aria-level=1.

Test thuan (doc file), chay tren staging host: python3 -m pytest.
Fail-before: moi assert deu do tren base (khong co injectHeadingSemantics).
"""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "sanpra_uiv16" / "public" / "js" / "sanpra_uiv16.js"
HOOKS = ROOT / "sanpra_uiv16" / "hooks.py"


class HeadingSemanticsP2bTest(unittest.TestCase):
    def test_inject_heading_semantics_exists(self):
        js = JS.read_text(encoding="utf-8")
        self.assertIn("function injectHeadingSemantics", js)

    def test_page_title_gets_role_heading(self):
        js = JS.read_text(encoding="utf-8")
        self.assertIn('setAttribute("role", "heading")', js)
        self.assertIn('setAttribute("aria-level", "1")', js)

    def test_called_on_desk_ready_and_page_change(self):
        js = JS.read_text(encoding="utf-8")
        # called twice: onDeskReady + page-change handler
        self.assertEqual(js.count("injectHeadingSemantics();"), 2)

    def test_p2b_bump_v(self):
        hooks = HOOKS.read_text(encoding="utf-8")
        self.assertIn("sanpra_uiv16.js?v=72", hooks)


if __name__ == "__main__":
    unittest.main()
