# -*- coding: utf-8 -*-
"""Guard z-index dropdown Link field phải thắng header datatable (fix 24/11/2026).

Nguyên nhân: comment trong CSS chon 20 nhung declaration dung var(--zi-raised)=10,
bằng .dt-header → browser fallback theo DOM order → report datatable de len dropdown.
Guard nay doc GIA TRI thuc trong rule co scope, khong soi chuoi roi rac.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "public" / "css" / "sanpra_uiv16.css"
HOOKS = ROOT / "hooks.py"


def rule_body(css: str, selector_fragment: str) -> str:
    clean = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", clean):
        if selector_fragment in m.group(1) and "awesomplete" in m.group(1):
            return m.group(2)
    return ""


def header_z(css: str) -> int:
    clean = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    m = re.search(r"--zi-raised:\s*(\d+)", clean)
    return int(m.group(1)) if m else -1


class TestReportDropdownZOrder(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.css = CSS.read_text(encoding="utf-8")

    def listbox_z(self) -> int:
        """Doc GIA TRI token thay vi soi literal (26/11: dua 20 vao --zi-listbox)."""
        m = re.search(r"--zi-listbox:\s*(\d+)", re.sub(r"/\*.*?\*/", "", self.css, flags=re.DOTALL))
        self.assertIsNotNone(m)
        assert m is not None
        return int(m.group(1))

    def test_listbox_z_index_20(self) -> None:
        body = rule_body(self.css, '[role="listbox"]')
        self.assertIn(
            "z-index: var(--zi-listbox)",
            body,
            "listbox phai dung token --zi-listbox=20 (khong phai var(--zi-raised)=10)",
        )
        self.assertEqual(self.listbox_z(), 20, "token --zi-listbox phai giu gia tri 20")

    def test_listbox_cao_hon_dt_header(self) -> None:
        self.assertGreater(self.listbox_z(), header_z(self.css), "listbox phai thang .dt-header")

    def test_cache_buster_tang(self) -> None:
        m = re.search(r"sanpra_uiv16\.css\?v=(\d+)", HOOKS.read_text(encoding="utf-8"))
        self.assertIsNotNone(m)
        assert m is not None
        self.assertGreaterEqual(int(m.group(1)), 83, "phai tang ?v de browser lay CSS moi")

    def test_guard_co_the_do(self) -> None:
        """Mutation: doi token ve --zi-raised=10 thi guard phai DO (bai hoc 61)."""
        mutated = self.css.replace("z-index: var(--zi-listbox) !important;", "z-index: var(--zi-raised) !important;")
        self.assertNotIn("z-index: var(--zi-listbox)", rule_body(mutated, '[role="listbox"]'))


if __name__ == "__main__":
    unittest.main()
