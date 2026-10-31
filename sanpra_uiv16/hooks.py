# ── APP METADATA ───────────────────────────────────────────────────────────────
app_name = "sanpra_uiv16"
app_title = "Sanpra UI V16"
app_publisher = "Sanpra"
app_description = "Professional white-label theme for Frappe/ERPNext"
app_email = "sales@sanpra.com"
app_license = "MIT"
app_color = "#E8610A"
app_icon = "octicon octicon-paintcan"
app_version = "2.5.0"

required_apps = []

# ── PUBLIC LOGIN ASSETS ────────────────────────────────────────────────────────
web_include_css = ["/assets/sanpra_uiv16/css/login.css?v=11"]
web_include_js = ["/assets/sanpra_uiv16/js/login_theme.js?v=9"]

# ── AUTHENTICATED DESK ASSETS ──────────────────────────────────────────────────
# Query versions are bumped whenever an asset changes to invalidate browser cache.
app_include_css = [
    "/assets/sanpra_uiv16/css/sanpra_uiv16.css?v=72",
    "/assets/sanpra_uiv16/css/sidebar.css?v=40",
    "/assets/sanpra_uiv16/css/command_palette.css?v=5",
    "/assets/sanpra_uiv16/css/smart_home.css?v=8",
    "/assets/sanpra_uiv16/css/notification_center.css?v=3",
    "/assets/sanpra_uiv16/css/polish.css?v=4",
    "/assets/sanpra_uiv16/css/dark_mode.css?v=17",
    "/assets/sanpra_uiv16/css/module_cards.css?v=2",
    "/assets/sanpra_uiv16/css/density.css?v=2",
    "/assets/sanpra_uiv16/css/theme_studio.css?v=19",
    "/assets/sanpra_uiv16/css/grid_row_slide_panel.css?v=1",
]
app_include_js = [
    "/assets/sanpra_uiv16/js/frappe_compat.js?v=2",
    "/assets/sanpra_uiv16/js/dark_mode.js?v=12",
    "/assets/sanpra_uiv16/js/personalization.js?v=1",
    "/assets/sanpra_uiv16/js/sanpra_uiv16.js?v=71",
    "/assets/sanpra_uiv16/js/sidebar.js?v=3",
    "/assets/sanpra_uiv16/js/command_palette.js?v=9",
    "/assets/sanpra_uiv16/js/notification_center.js?v=4",
    "/assets/sanpra_uiv16/js/module_cards.js?v=10",
    "/assets/sanpra_uiv16/js/theme_runtime.js?v=8",
    "/assets/sanpra_uiv16/js/chart_runtime.js?v=4",
    "/assets/sanpra_uiv16/js/grid_row_slide_panel.js?v=1",
]

# ── BOOT / INSTALL / DOCUMENT LIFECYCLE HOOKS ──────────────────────────────────
boot_session = "sanpra_uiv16.boot.add_boot_data"

after_install = "sanpra_uiv16.setup.after_install"
after_migrate = "sanpra_uiv16.setup.after_migrate"

doc_events = {
    "Theme Settings": {
        "on_update": "sanpra_uiv16.events.theme_settings_on_update",
    },
    "Company": {
        "after_insert": "sanpra_uiv16.events.company_after_insert",
    },
}
