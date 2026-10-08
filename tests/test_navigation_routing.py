"""Regression coverage for Desk SPA navigation race conditions."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_CARDS = ROOT / "sanpra_uiv16" / "public" / "js" / "module_cards.js"
DESK_JS = ROOT / "sanpra_uiv16" / "public" / "js" / "sanpra_uiv16.js"
PALETTE = ROOT / "sanpra_uiv16" / "public" / "js" / "command_palette.js"
HOOKS = ROOT / "sanpra_uiv16" / "hooks.py"


class NavigationRoutingTest(unittest.TestCase):
    def test_delayed_apps_grid_is_cancelled_after_route_changes(self):
        js = MODULE_CARDS.read_text(encoding="utf-8")

        self.assertIn("_routeGeneration", js)
        self.assertIn("_activePoller", js)
        self.assertIn("generation !== _routeGeneration", js)
        self.assertIn("frappe.container.page.contains(container)", js)
        self.assertIn('container.querySelector("#st-module-grid")', js)
        self.assertNotIn('cards[j].addEventListener("click"', js)

    def test_apps_grid_preserves_workspace_dom_and_syncs_smart_home_route(self):
        js = MODULE_CARDS.read_text(encoding="utf-8")

        self.assertIn("hideRealWorkspaceContent(container)", js)
        self.assertIn("restoreRealWorkspaceContent()", js)
        self.assertIn("data-st-hidden-by-grid", js)
        self.assertNotIn("container.innerHTML =", js)
        self.assertIn("smartHomeOverrideActive()", js)
        self.assertIn("frappe.set_route(frappe.boot.home_page)", js)

    def test_startup_does_not_override_frappe_deep_links(self):
        js = DESK_JS.read_text(encoding="utf-8")

        self.assertNotIn("isEmptyOrWorkspace", js)
        self.assertIn("bootinfo.home_page owns the initial Smart Home redirect", js)

    def test_command_palette_uses_real_workspace_slug(self):
        js = PALETTE.read_text(encoding="utf-8")

        self.assertIn("page.route ||", js)
        self.assertNotIn('frappe.set_route("workspace", encodeURIComponent(page.name))', js)

    def test_navigation_assets_are_cache_busted(self):
        hooks = HOOKS.read_text(encoding="utf-8")

        self.assertIn("/assets/sanpra_uiv16/js/sanpra_uiv16.js?v=67", hooks)
        self.assertIn("/assets/sanpra_uiv16/js/command_palette.js?v=9", hooks)
        self.assertIn("/assets/sanpra_uiv16/js/module_cards.js?v=10", hooks)


if __name__ == "__main__":
    unittest.main()
