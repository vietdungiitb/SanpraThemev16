"""UI-MODAL-HEADER 26/11 — DocType Settings phải nổi trên toolbar cố định.

Triệu chứng đo live-DOM trên staging: `#st-top-toolbar` z-index 1060 (theme
`--zi-overlay`) > `.modal` 1050 (Bootstrap) ⇒ phủ 11px đỉnh `.modal-dialog`.
Guard fail-before: CSS hiện tại chưa có rule => ĐỎ. Sau fix => XANH.

Lesson 75: đổi asset phải bump `?v=` trong hooks.py.
Lesson 61: assert trên GIÁ TRỊ (block CSS chứa token), không trên tên hàm.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "sanpra_uiv16.css"
HOOKS = ROOT / "sanpra_uiv16" / "hooks.py"


def block_after(text: str, needle: str, size: int = 220) -> str:
    i = text.index(needle)
    return text[i : i + size]


class SettingsDialogZIndexTest(unittest.TestCase):
    def test_dialog_duoc_nang_len_vi_modal(self):
        """Fail-before: chua co rule scoped => test do."""
        css = CSS.read_text(encoding="utf-8")
        self.assertIn(".modal.settings-dialog-wrapper", css)
        self.assertIn("z-index: var(--zi-modal)", block_after(css, ".modal.settings-dialog-wrapper"))

    def test_backdrop_duoc_nang_len_vi_editor(self):
        """Fail-before: backdrop van 1040 (dup toolbar 1060) => test do."""
        css = CSS.read_text(encoding="utf-8")
        self.assertIn("z-index: var(--zi-editor)", block_after(css, ".modal-backdrop.show"))

    def test_asset_version_duoc_bump(self):
        """Lesson 75: khong bump ?v= thi staging van serve CSS cu (khong ghim cung so)."""
        hooks = HOOKS.read_text(encoding="utf-8")
        m = re.search(r"sanpra_uiv16\.css\?v=(\d+)", hooks)
        self.assertIsNotNone(m)
        assert m is not None
        self.assertGreaterEqual(int(m.group(1)), 84, "phai tang ?v de browser lay CSS moi")


if __name__ == "__main__":
    unittest.main()
