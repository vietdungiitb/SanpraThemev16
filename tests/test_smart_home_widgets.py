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
        self.assertIn("st_smart_home_layout_v3::", js)
        self.assertNotIn("st_smart_home_layout_v2::", js)

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

    def test_default_order_follows_user_priority(self):
        """Thu tu mac dinh: bo 3 hanh dong -> ops -> recent/quick -> apps cuoi."""
        js = JS.read_text(encoding="utf-8")
        body = js.split("_render_widgets() {", 1)[1].split("this._render_quick_create();", 1)[0]
        markers = [
            '"today-focus"',
            '"needs-attention"',
            '"reports-charts"',
            '"giam-sat-van-hanh"',
            '"recent-documents"',
            '"quick-create"',
            '"your-apps"',
        ]
        positions = [body.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))
        # Khong con migration dat your-apps sau KPI (key v3 = layout moi).
        self.assertNotIn("predate the upstream apps launcher", js)

    def test_trio_cards_share_equal_height(self):
        """F1: 3 card half cung hang thang day nhau (stretch + full height)."""
        css = CSS.read_text(encoding="utf-8")
        self.assertIn("align-items: stretch", css)
        self.assertIn("height: 100%", css)

    def test_report_charts_deep_link_to_chart_docs(self):
        """F2: bieu do link thang Dashboard Chart doc, khong ve workspace chung."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn('"/desk/dashboard-chart/"', js)
        self.assertNotIn('route: "/desk/" + slug', js)

    def test_report_charts_has_six_entries(self):
        """Anh 3: 6 nut lap day o trong (2 report + 2 chart + 2 chung tu)."""
        js = JS.read_text(encoding="utf-8")
        for label in (
            "hieu-qua-giao-vien",
            "hoc-phi-den-han-hom-nay",
            "dashboard-chart",
            '"/desk/sales-invoice"',
            '"/desk/payment-entry"',
        ):
            self.assertIn(label, js)

    def test_app_cards_are_centered(self):
        """Card luoi ung dung: icon + tieu de can giua (module_cards.css)."""
        root = Path(__file__).resolve().parents[1]
        css = (root / "sanpra_uiv16" / "public" / "css" / "module_cards.css").read_text(encoding="utf-8")
        hooks = (root / "sanpra_uiv16" / "hooks.py").read_text(encoding="utf-8")
        card_block = css.split(".st-ws-card {", 1)[1].split("}", 1)[0]
        self.assertIn("align-items: center", card_block)
        self.assertIn("text-align: center", card_block)
        # Center co tu d054ecb nhung thieu bump -> browser giu ban cu: khoa bang version.
        # (Guard test_test_files_utf8 cam ghim so ?v= cu the: parse dong thay vi ghim.)
        import re as _re
        _m = _re.search(r"module_cards\.css\?v=(\d+)", hooks)
        self.assertIsNotNone(_m, "thieu version module_cards.css trong hooks")
        self.assertGreaterEqual(int(_m.group(1)), 3)

    def test_ops_click_matches_any_route_segment(self):
        """F3: URL canonical co shell dung truoc nen so khop tren moi doan."""
        root = Path(__file__).resolve().parents[1]
        desk_js = (root / "sanpra_uiv16" / "public" / "js" / "sanpra_uiv16.js").read_text(encoding="utf-8")
        self.assertIn("on_ops_page", desk_js)
        self.assertIn("location.pathname", desk_js)
        self.assertNotIn("route[0] !== want", desk_js)

    def test_ops_widget_has_live_body_and_links(self):
        """O Giam sat khong duoc trong: body lay get_ops_summary + link ve workspace."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn("st-sh-ops-stats", js)
        self.assertIn("get_ops_summary", js)
        self.assertIn("job_status_summary", js)
        self.assertIn("_refresh_ops", js)

    def test_two_half_widgets_balance_attention_row(self):
        """Hang cuoi: needs-attention + 2 widget half = 4+4+4 khit hang."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn('"today-focus"', js)
        self.assertIn('"reports-charts"', js)
        self.assertIn("_refresh_today", js)
        self.assertIn("_render_reports_charts", js)

    def test_workspace_click_map_covers_all_real_card_names(self):
        """Mo phong st_norm_vi (JS) tren 13 nhan the that do user do duoc:
        moi ten deu phai ra key co trong ST_OPS_CARD_ROUTES."""
        import re
        import unicodedata
        root = Path(__file__).resolve().parents[1]
        desk_js = (root / "sanpra_uiv16" / "public" / "js" / "sanpra_uiv16.js").read_text(encoding="utf-8")

        def st_norm_vi(value):
            s = str(value or "").lower()
            s = unicodedata.normalize("NFD", s)
            s = "".join(c for c in s if unicodedata.category(c) != "Mn")
            return s.replace("đ", "d").replace(" ", "-").strip()

        # Route that tren browser user (F3 that): [shell, ten giu dau cach].
        self.assertEqual(st_norm_vi("Giám sát vận hành"), "giam-sat-van-hanh")

        m = re.search(r"ST_OPS_CARD_ROUTES\s*=\s*\{(.*?)\};", desk_js, re.S)
        self.assertIsNotNone(m)
        keys = set(re.findall(r'"([^"]+)"\s*:', m.group(1)))
        names = [
            "Việc mở toàn hệ thống",
            "Việc quá hạn toàn hệ thống",
            "Sự kiện hôm nay",
            "Lỗi 24 giờ",
            "Job lỗi 24 giờ",
            "Số học viên đang học",
            "Số lớp đang mở",
            "Lead mới từ đầu tháng",
            "Doanh thu ngày qua",
            "Điểm danh hôm nay",
            "Lead mới hôm nay",
            "Tổng công nợ chưa thu",
            "Công nợ quá hạn",
        ]
        self.assertEqual(len(names), 13)
        for name in names:
            self.assertIn(st_norm_vi(name), keys, name)

    def test_workspace_number_cards_have_click_map(self):
        """13 the so GSVH co map ve route: 6 snapshot + 5 ops + 2 finance."""
        root = Path(__file__).resolve().parents[1]
        desk_js = (root / "sanpra_uiv16" / "public" / "js" / "sanpra_uiv16.js").read_text(encoding="utf-8")
        # EditorJS number_card block dat `number_card_name` = nhan the (block.js)
        self.assertIn("ST_OPS_CARD_ROUTES", desk_js)
        self.assertIn("number_card_name", desk_js)
        self.assertIn("console.warn", desk_js)
        for key in (
            "viec-mo-toan-he-thong",
            "viec-qua-han-toan-he-thong",
            "su-kien-hom-nay",
            "loi-24-gio",
            "job-loi-24-gio",
            "so-hoc-vien-dang-hoc",
            "so-lop-dang-mo",
            "lead-moi-tu-dau-thang",
            "doanh-thu-ngay-qua",
            "diem-danh-hom-nay",
            "lead-moi-hom-nay",
            "tong-cong-no-chua-thu",
            "cong-no-qua-han",
        ):
            self.assertIn('"' + key + '"', desk_js)

    def test_no_pii_in_new_widgets(self):
        """Widget moi chi dem, khong subject/email/ten (S7)."""
        js = JS.read_text(encoding="utf-8")
        self.assertNotIn("subject", js)
        self.assertNotIn("for_user", js)

    def test_open_tasks_kpi_scoped_to_user(self):
        """open-todos KPI phai loc allocated_to=user (cung lop bug O1 cua my-todos)."""
        js = JS.read_text(encoding="utf-8")
        block = js.split('id: "open-tasks"', 1)[1].split("},", 1)[0]
        self.assertIn("allocated_to: frappe.session.user", block)

    def test_today_focus_no_duplicate_counts(self):
        """today-focus render viec tiep theo (link ban ghi), khong dem so;
        trong -> thu gon all-clear thay vi 4 dong 0."""
        js = JS.read_text(encoding="utf-8")
        body = js.split("_refresh_today() {", 1)[1].split("_render_reports_charts", 1)[0]
        self.assertIn("frappe.client.get_list", body)
        self.assertNotIn("st-sh-pending-count", body)
        self.assertNotIn("Việc mở của tôi", body)
        self.assertIn("st-sh-all-clear", body)

    def test_pending_includes_overdue_fees(self):
        """Fees khong co status -> loc due_date + outstanding_amount."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn('dt: "Fees"', js)
        self.assertIn("due_date", js)
        self.assertIn("outstanding_amount", js)
        self.assertIn("overdue tuition fees", js)

    def test_reports_charts_renders_chart_container(self):
        """Chart that qua frappe.Chart + dashboard_chart.get; thieu -> fallback link."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn("frappe.Chart", js)
        self.assertIn("dashboard_chart.dashboard_chart.get", js)
        self.assertIn("st-sh-chart-canvas", js)
        self.assertIn("st-sh-rc-links", js)

    def test_apps_grid_filters_technical(self):
        """Luoi apps an 7 tile ky thuat tieng Anh (PM quyet 10/11/2026)."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn("HIDDEN_APPS", js)
        for name in ("build", "hr setup", "tenure", "invoicing", "payments", "recruitment", "accounting"):
            self.assertIn('"' + name + '"', js)
        # Khoa dung that, khong chi ton tai: filter phai duoc ap vao slice.
        self.assertIn("HIDDEN_APPS.indexOf(normTitle", js)
        self.assertIn("visible.slice(0, 12)", js)
        self.assertNotIn("(pages || []).slice(0, 12)", js)

    def test_recent_skips_user_doctype(self):
        """recent-documents bo qua User (docname la email)."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn('route[1] !== "User"', js)

    def test_greeting_date_uses_site_lang(self):
        """Ngay theo site lang (vi -> vi-VN), khong theo locale trinh duyet."""
        js = JS.read_text(encoding="utf-8")
        self.assertIn("_site_locale()", js)
        self.assertIn('"vi-VN"', js)
        self.assertNotIn("toLocaleDateString(undefined", js)


if __name__ == "__main__":
    unittest.main()
