"""Unit test cho script trich xuat __() (T101).

Quy uoc theo fork: unittest + Path(__file__).parents[1] lam ROOT, nap script
bang spec_from_file_location (khong phu thuoc package layout).
Chay: python -m pytest sanpra_uiv16/tools/test_extract_i18n.py -q (tu root fork)
"""

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SCRIPT = TOOLS / "extract_i18n.py"


def load_script():
    spec = importlib.util.spec_from_file_location("extract_i18n_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExtractI18nTest(unittest.TestCase):
    def test_script_ton_tai_va_nap_duoc(self):
        """Fail-before: do khi extract_i18n.py chua ton tai."""
        self.assertTrue(SCRIPT.exists(), f"thieu {SCRIPT}")
        mod = load_script()
        for name in ("extract_calls", "load_covered", "compute_report"):
            self.assertTrue(callable(getattr(mod, name, None)), f"thieu ham {name}")

    def test_trich_dung_tren_cay_mau(self):
        """Fixture: 2 file mau (js + py) + 1 csv mau -> so phai khop tay."""
        mod = load_script()
        tmp = tempfile.mkdtemp(prefix="t101_")
        root = Path(tmp)
        try:
            (root / "a").mkdir(parents=True, exist_ok=True)
            (root / "a" / "one.js").write_text(
                'x = __("Hello world");\ny = __("Save");\nz = __("Hello world");\n',
                encoding="utf-8",
            )
            (root / "a" / "two.py").write_text(
                'a = __("Save")\nb = __(\n    "Multiline string"\n)\n',
                encoding="utf-8",
            )
            (root / "a" / "vi.csv").write_text(
                '"Hello world","Xin chao the gioi"\n', encoding="utf-8"
            )
            calls = mod.extract_calls(root)
            distinct = sorted({c[0] for c in calls})
            self.assertEqual(distinct, ["Hello world", "Multiline string", "Save"])
            covered = mod.load_covered(root / "a" / "vi.csv")
            self.assertEqual(covered, {"Hello world"})
            report = mod.compute_report(root, csv_path=root / "a" / "vi.csv")
            self.assertEqual(report["distinct"], 3)
            self.assertEqual(report["covered"], 1)
            self.assertEqual(report["missing"], 2)
            self.assertEqual(sorted(report["missing_list"]), ["Multiline string", "Save"])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_parse_csv_chiu_duoc_dau_phay_trong_chuoi(self):
        """CSV quote-aware: dau phay trong chuoi khong tach cot sai."""
        mod = load_script()
        tmp = tempfile.mkdtemp(prefix="t101csv_")
        root = Path(tmp)
        try:
            root.mkdir(parents=True, exist_ok=True)
            (root / "vi.csv").write_text(
                '"Save, and continue","Luu, va tiep tuc"\n"Plain","Don gian"\n',
                encoding="utf-8",
            )
            covered = mod.load_covered(root / "vi.csv")
            self.assertEqual(covered, {"Save, and continue", "Plain"})
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_thu_muc_tools_khong_bi_quet(self):
        """Script khong tu-dem-chinh-minh: __() trong tools/ bi loai."""
        mod = load_script()
        tmp = tempfile.mkdtemp(prefix="t101skip_")
        root = Path(tmp)
        try:
            (root / "tools").mkdir(parents=True, exist_ok=True)
            (root / "tools" / "tool.js").write_text('x = __("Tool string");\n', encoding="utf-8")
            (root / "app.js").write_text('y = __("App string");\n', encoding="utf-8")
            calls = mod.extract_calls(root)
            distinct = sorted({c[0] for c in calls})
            self.assertEqual(distinct, ["App string"])
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_brand_whitelist_duoc_tru_khoi_missing(self):
        """R-01: brand terms explicit trong script, khong tinh vao missing."""
        mod = load_script()
        self.assertTrue(len(mod.BRAND_WHITELIST) > 0, "BRAND_WHITELIST rong")
        report = {
            "distinct": 2,
            "covered": 0,
            "missing": 2,
            "missing_list": ["Smart Education", "Can thieu that"],
        }
        adjusted = mod.apply_whitelist(report)
        self.assertIn("Smart Education", adjusted["whitelisted"])
        self.assertEqual(adjusted["missing"], 1)
        self.assertEqual(adjusted["missing_list"], ["Can thieu that"])


if __name__ == "__main__":
    unittest.main()
