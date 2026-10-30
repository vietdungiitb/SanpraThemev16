"""Coverage i18n: moi __() trong fork phai co trong vi.csv (T101).

Guard chong tai lui: them __() moi ma quen dich -> test nay do.
Chay tu root fork: python -m pytest sanpra_uiv16/tests/test_theme_i18n_coverage.py -q
"""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "sanpra_uiv16" / "tools"
SCRIPT = TOOLS / "extract_i18n.py"


def load_script():
    spec = importlib.util.spec_from_file_location("extract_i18n_coverage", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class I18nCoverageTest(unittest.TestCase):
    def test_missing_bang_0_sau_tru_brand(self):
        mod = load_script()
        report = mod.compute_report(ROOT)
        adjusted = mod.apply_whitelist(report)
        self.assertEqual(
            adjusted["missing"],
            0,
            f"con {adjusted['missing']} chuoi thieu dich: "
            + ", ".join(repr(s) for s in adjusted["missing_list"][:10]),
        )


if __name__ == "__main__":
    unittest.main()
