"""Slice 6 — sticky tab không được cắt tiêu đề section khi cuộn form."""

import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "sanpra_uiv16.css"
JS = ROOT / "sanpra_uiv16" / "public" / "js" / "sanpra_uiv16.js"
VI = ROOT / "sanpra_uiv16" / "translations" / "vi.csv"


class FormScrollMarginTest(unittest.TestCase):
    def test_section_head_co_scroll_margin_top(self):
        css = CSS.read_text(encoding="utf-8")
        self.assertIn("scroll-margin-top", css)
        self.assertTrue(re.search(r".form-section[^}]*scroll-margin-top", css))

    def test_topbar_dung_nhan_ban_lam_viec(self):
        js = JS.read_text(encoding="utf-8")
        self.assertIn('frappe._("Desk Workspace")', js)
        vi = VI.read_text(encoding="utf-8")
        self.assertIn('"Desk Workspace","Bàn làm việc"', vi)


if __name__ == "__main__":
    unittest.main()
