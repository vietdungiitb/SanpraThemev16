"""Slice P2-d A — sub-11px typography floor (11px).

Guard: khong con khai bao `font-size` < 11px trong fork CSS, tru danh sach
whitelist ghi ly do (hien tai: khong co). Moi khai bao 9px/10px phai duoc
nang len toi thieu 11px de dam bao doc (AUDIT_UI_FULL 31/10/2026: 30 khai
bao = 10px x24 + 9px x6).

Lesson 75: khi sua asset phai bump ?v= trong hooks.py + cap nhat test ghim
version. Lesson 61: assert tren gia tri (count), khong tren tap ten ham.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_DIR = ROOT / "sanpra_uiv16" / "public" / "css"

# Whitelist: (file, line) khai bao duoc phep < 11px, kem ly do.
# Hien tai rong — moi truong hop can them phai ghi ly do cu the.
WHITELIST = set()


class Sub11pxTypographyTest(unittest.TestCase):
    def _collect(self):
        offenders = []
        for path in sorted(CSS_DIR.rglob("*.css")):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for m in re.finditer(r"font-size\s*:\s*(\d+(?:\.\d+)?)\s*px", line, re.I):
                    if float(m.group(1)) < 11 and (str(path.relative_to(ROOT)), lineno) not in WHITELIST:
                        offenders.append((str(path.relative_to(ROOT)), lineno, m.group(0), line.strip()))
        return offenders

    def test_no_sub_11px_font_size_in_fork_css(self):
        """Fail-before tren code cu (30 khai bao). Sau fix: count == 0."""
        offenders = self._collect()
        self.assertEqual(
            len(offenders),
            0,
            "Con {} khai bao font-size < 11px:\n{}".format(
                len(offenders),
                "\n".join("  {}:{} {}  ({})".format(*o) for o in offenders[:20]),
            ),
        )


if __name__ == "__main__":
    unittest.main()