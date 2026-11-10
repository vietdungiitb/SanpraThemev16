"""Structural guard for the system-root sidebar shown on ``/desk/smart-home``.

The page is the desk's home. Its shell must be named after the page so the router
leaves the URL alone (a shell whose slug equals the route's first segment writes no
prefix), and its rows must describe the whole system instead of the theme settings.
"""

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
SIDEBAR = ROOT / "sanpra_uiv16" / "sanpra_ui_v16" / "sidebar" / "smart_home" / "smart_home.json"
PAGE = "smart-home"


class HomeSidebarTest(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(SIDEBAR.read_text(encoding="utf-8"))

    def test_shell_is_named_after_the_page_it_decorates(self):
        self.assertEqual(self.doc["doctype"], "Sidebar")
        self.assertEqual(self.doc["title"], "Smart Home")
        self.assertEqual(self.doc["name"], "Smart Home")
        self.assertEqual(self.doc["module"], "Sanpra UI V16")
        self.assertEqual(self.doc["standard"], 1)
        # Frappe writes the shell's slug into the URL; equal slugs mean no `/desk/<shell>/` prefix.
        self.assertEqual(self.doc["title"].lower().replace(" ", "-"), PAGE)

    def test_page_is_claimed_by_this_shell_only(self):
        claims = [i for i in self.doc["items"] if i.get("link_type") == "Page" and i.get("link_to") == PAGE]

        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0]["is_default_module"], 1)

    def test_navigation_covers_the_system_not_the_theme_settings(self):
        labels = {i.get("label") for i in self.doc["items"]}
        targets = {(i.get("link_type"), i.get("link_to")) for i in self.doc["items"]}

        self.assertIn("Giám sát vận hành", labels)
        self.assertIn(("Workspace", "Giám sát vận hành"), targets)
        self.assertIn(("Workspace", "Giáo dục thông minh"), targets)
        self.assertIn(("Page", "all-apps"), targets)
        self.assertNotIn(("DocType", "Theme Settings"), targets)
        self.assertNotIn(("Page", "theme-studio"), targets)


if __name__ == "__main__":
    unittest.main()
