"""Desktop gọn: 1 header + nhãn rail/tile đầy đủ, không cắt/lẫn ngôn ngữ."""

import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "sanpra_uiv16" / "public" / "js" / "sanpra_uiv16.js"
SIDEBAR_CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "sidebar.css"
DESK_CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "sanpra_uiv16.css"


class DesktopNavTest(unittest.TestCase):
    def test_rail_labels_di_qua_dich(self):
        """Nhãn rail phải bọc __() như grid core (không EN/VI lẫn)."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn("__(item.title", js)
        self.assertNotIn("esc(item.title) + '</span></a>'", js)

    def test_rail_khong_tach_giua_tu_va_nut_thu_gon_luon_thay(self):
        """Rail 72px: wrap theo dấu cách, không tách giữa từ + nút collapse dính đáy."""
        css = SIDEBAR_CSS.read_text(encoding="utf-8")
        label = css.split("#st-icon-rail .st-rail-app-label {")[1].split("}")[0]
        self.assertIn("word-break", label)
        self.assertIn("keep-all", label)
        self.assertNotIn("anywhere", label)
        self.assertIn("overflow-y", css)
        segs = css.split("#st-icon-rail .st-rail-collapse {")[1:]
        self.assertTrue(
            any("flex-shrink" in s.split("}")[0] and "min-height" in s.split("}")[0] for s in segs),
            "nut collapse phai flex-shrink:0 trong rule co min-height (khong bi day mat)",
        )


    def test_card_break_header_khac_biet_muc_con(self):
        """F0 UAT mat nguoi: Card Break render <a> KHONG href (sidebar_item.js
        chi sinh path cho type Link) nen CSS phan biet duoc bang :not([href]).
        Workspace Link validate chi cho Link/Card Break — cam doi fixture
        sang Section Break (migrate chet ValidationError)."""
        css = SIDEBAR_CSS.read_text(encoding="utf-8")
        self.assertIn(".item-anchor:not([href]) .sidebar-item-label", css)
        rule = css.split(".item-anchor:not([href]) .sidebar-item-label {")[1].split("}")[0]
        self.assertIn("text-transform", rule)
        self.assertIn("uppercase", rule)
    def test_an_thanh_duoi_header_tren_trang_desktop(self):
        """Chỉ giữ navbar: ẩn .desktop-navbar (logo+search+bell+avatar trùng)."""
        css = DESK_CSS.read_text(encoding="utf-8")
        self.assertIn("#page-desktop .desktop-navbar", css)
        seg = css.split("#page-desktop .desktop-navbar")[1].split("}")[0]
        self.assertIn("display", seg)
        self.assertIn("none", seg)

    def test_tile_desktop_hien_2_dong_khong_cat(self):
        """Tile grid hiện đủ tên app dài (Smart Edu Core, Quản lý tuyển sinh...)."""
        css = DESK_CSS.read_text(encoding="utf-8")
        self.assertIn(".icon-caption .icon-title", css)
        seg = css.split(".icon-caption .icon-title")[1].split("}")[0]
        self.assertIn("line-clamp", seg)

    def test_css_desktop_duoc_nap_co_cache_bust(self):
        """sanpra_uiv16.css phải có version mới để trình duyệt nhận CSS desktop."""
        from pathlib import Path as _P
        hooks = (_P(__file__).resolve().parents[1] / "sanpra_uiv16" / "hooks.py").read_text(encoding="utf-8")
        self.assertIn("/assets/sanpra_uiv16/css/sanpra_uiv16.css?v=75", hooks)


if __name__ == "__main__":
    unittest.main()
