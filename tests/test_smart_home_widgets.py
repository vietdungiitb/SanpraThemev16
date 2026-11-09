"""Structural regression coverage for Smart Home's persistent widget layout."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "sanpra_uiv16" / "sanpra_ui_v16" / "page" / "smart_home" / "smart_home.js"
CSS = ROOT / "sanpra_uiv16" / "public" / "css" / "smart_home.css"
HOOKS = ROOT / "sanpra_uiv16" / "hooks.py"


class SmartHomeWidgetsTest(unittest.TestCase):
    def test_dashboard_is_built_from_reorderable_widgets(self):
        js = JS.read_text(encoding="utf-8")

        self.assertIn("st-sh-widget-grid", js)
        self.assertIn('data-widget-id="', js)
        self.assertIn('draggable="false"', js)
        self.assertIn("dragstart.st_sh_layout", js)
        self.assertIn("dragover.st_sh_layout", js)
        self.assertIn("drop.st_sh_layout", js)
        self.assertIn("st_smart_home_layout_v2::", js)

    def test_layout_has_customize_reset_and_accessible_move_controls(self):
        js = JS.read_text(encoding="utf-8")

        self.assertIn("Customize layout", js)
        self.assertIn("Reset your Smart Home widget order?", js)
        self.assertIn("Move backward", js)
        self.assertIn("Move forward", js)
        self.assertIn('aria-live="polite"', js)

    def test_widget_grid_is_responsive_and_theme_aware(self):
        css = CSS.read_text(encoding="utf-8")

        self.assertIn("grid-template-columns: repeat(12", css)
        self.assertIn('[data-widget-size="quarter"]', css)
        self.assertIn('[data-widget-size="wide"]', css)
        self.assertIn("html[data-theme=\"dark\"]", css)
        self.assertIn("@media (max-width: 560px)", css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)

    def test_smart_home_asset_cache_is_bumped(self):
        hooks = HOOKS.read_text(encoding="utf-8")
        self.assertRegex(hooks, r"/assets/sanpra_uiv16/css/smart_home\.css\?v=\d+")

    def test_widget_library_and_simple_builder_are_available(self):
        js = JS.read_text(encoding="utf-8")
        css = CSS.read_text(encoding="utf-8")

        self.assertIn("Add widgets", js)
        self.assertIn("Build your own", js)
        self.assertIn("data-template-id", js)
        self.assertIn("st-sh-builder-form", js)
        self.assertIn("_create_custom_widget", js)
        self.assertIn("library_drag_id", js)
        self.assertIn(".st-sh-library", css)
        self.assertIn(".st-sh-builder", css)

    def test_custom_widgets_are_saved_per_user(self):
        js = JS.read_text(encoding="utf-8")

        self.assertIn("state.custom", js)
        self.assertIn("state.added", js)
        self.assertIn("state.hidden", js)
        self.assertIn("JSON.stringify(this.state)", js)

    def test_widget_width_can_be_changed_and_persisted(self):
        js = JS.read_text(encoding="utf-8")
        css = CSS.read_text(encoding="utf-8")

        self.assertIn("Make widget narrower", js)
        self.assertIn("Make widget wider", js)
        self.assertIn("_resize_widget", js)
        self.assertIn("this.state.sizes", js)
        self.assertIn('[data-widget-size="medium"]', css)
        self.assertIn('[data-widget-size="full"]', css)

    def test_my_todos_kpi_is_scoped_to_current_user(self):
        """My ToDos phải scope allocated_to=frappe.session.user — ToDo read
        permission là role All, filter chỉ status:Open sẽ đếm toàn site."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn('filters: { status: "Open", allocated_to: frappe.session.user }', js)
        self.assertNotIn(
            'id: "my-todos",\n\t\t\t\tlabel: __("My ToDos"),\n\t\t\t\tdt: "ToDo",\n\t\t\t\tfilters: { status: "Open" },',
            js,
        )

    def test_personal_kpis_render_before_system_kpis(self):
        """Lớp 1 (việc cá nhân) lên trước lớp hệ thống trong default order."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn('personal_ids = ["my-todos", "open-tasks"]', js)
        self.assertIn("personal_ids.indexOf", js)
        self.assertIn("Layer 1 (personal)", js)

    def test_apps_grid_shows_12_and_ops_widget_is_viewer_gated(self):
        js = JS.read_text(encoding="utf-8")
        self.assertIn("slice(0, 12)", js)
        self.assertIn('_ops_widget', js)
        self.assertIn('data-widget-id="giam-sat-van-hanh"', js)
        self.assertIn("self._ops_workspace_name", js)


if __name__ == "__main__":
    unittest.main()
