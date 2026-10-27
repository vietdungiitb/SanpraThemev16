"""S5: moi @frappe.whitelist trong theme_api.py phai khai methods ro rang.

PUT/DELETE khong duoc phep: endpoint GHI chi nhan POST (chong CSRF qua GET),
endpoint DOC nhan GET+POST (caller JS dung frappe.call = POST; doc can GET con
tra 200 theo AC-02). Kiem bang AST tinh — khong import frappe.
"""

import ast
import unittest
from pathlib import Path


THEME_API = Path(__file__).resolve().parents[1] / "sanpra_uiv16" / "theme_api.py"

# 4 endpoint DOC (duoc GET): con lai 9 endpoint GHI (chi POST).
READ_ENDPOINTS = {
    "get_theme_studio_state",
    "get_chart_preview",
    "preview_theme_css",
    "get_resolved_theme_runtime",
}

EXPECTED_METHODS = {
    "get_theme_studio_state": ["GET", "POST"],
    "get_chart_preview": ["GET", "POST"],
    "preview_theme_css": ["GET", "POST"],
    "save_theme_draft": ["POST"],
    "publish_theme_config": ["POST"],
    "manage_theme_profile": ["POST"],
    "restore_theme_version": ["POST"],
    "import_theme_profile": ["POST"],
    "save_theme_assignments": ["POST"],
    "save_theme_schedule": ["POST"],
    "set_user_theme_profile": ["POST"],
    "get_resolved_theme_runtime": ["GET", "POST"],
    "clear_theme_cache": ["POST"],
}


def whitelist_methods():
    """{ten ham: methods} cho moi ham co @frappe.whitelist; None = bare."""
    tree = ast.parse(THEME_API.read_text(encoding="utf-8"))
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            func = getattr(dec, "func", None)
            if isinstance(dec, ast.Call) and getattr(func, "attr", "") == "whitelist":
                methods = None
                for kw in dec.keywords:
                    if kw.arg == "methods":
                        methods = ast.literal_eval(kw.value)
                out[node.name] = methods
    return out


class ThemeApiMethodsTest(unittest.TestCase):
    def test_moi_whitelist_khai_methods(self):
        """Khong con @frappe.whitelist() bare — thieu methods la do S5."""
        found = whitelist_methods()
        self.assertEqual(len(found), 13, "cho 13 whitelist (bare + khai), thuc te: %r" % (found,))
        bare = sorted(n for n, m in found.items() if m is None)
        self.assertEqual(bare, [], "con whitelist bare (thieu methods=): %r" % (bare,))

    def test_mapping_methods_dung_quy_uoc_doc_ghi(self):
        """4 DOC = GET+POST; 9 GHI = POST (PUT/DELETE bi cam)."""
        found = whitelist_methods()
        self.assertEqual(set(found), set(EXPECTED_METHODS), "lech tap endpoint: %r" % (found,))
        for name, want in EXPECTED_METHODS.items():
            self.assertEqual(
                found[name], want, "%s: cho %r, thuc te %r" % (name, want, found[name])
            )
            for m in found[name]:
                self.assertIn(m, ("GET", "POST"), "%s: method la %r" % (name, m))


if __name__ == "__main__":
    unittest.main()
