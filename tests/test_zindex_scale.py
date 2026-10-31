"""Slice P2-d B — z-index scale 6 cap.

Guard: khong con khai bao `z-index` voi gia tri literal (khong qua var(--zi-*)).
Tat ca phai di qua 1 trong 6 token: --zi-base, --zi-raised, --zi-overlay,
--zi-editor, --zi-modal, --zi-top. (AUDIT_UI_FULL 31/10/2026: ~25-27 gia tri
roi rac.)

Lesson 75: sua asset phai bump ?v= trong hooks.py + cap nhat test ghim.
Lesson 61: assert tren gia tri (count), khong tren tap ten ham.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_DIR = ROOT / "sanpra_uiv16" / "public" / "css"
TOKENS_FILE = ROOT / "sanpra_uiv16" / "public" / "css" / "sanpra_uiv16.css"

TOKENS = ("--zi-base", "--zi-raised", "--zi-overlay", "--zi-editor", "--zi-modal", "--zi-top")


class ZIndexScaleTest(unittest.TestCase):
    def _literal_count(self):
        n = 0
        for path in sorted(CSS_DIR.rglob("*.css")):
            for line in path.read_text(encoding="utf-8").splitlines():
                for m in re.finditer(r"z-index\s*:\s*([^\s;]+)", line, re.I):
                    val = m.group(1)
                    if not val.startswith("var("):
                        n += 1
        return n

    def test_no_literal_z_index_outside_tokens(self):
        """Fail-before tren code cu (~54 khai bao literal). Sau fix: count == 0."""
        n = self._literal_count()
        self.assertEqual(n, 0, "Con {} khai bao z-index literal (khong qua var(--zi-*))".format(n))

    def test_six_level_tokens_defined(self):
        text = TOKENS_FILE.read_text(encoding="utf-8")
        for tok in TOKENS:
            self.assertIn(tok, text, "Thieu token {}".format(tok))


if __name__ == "__main__":
    unittest.main()