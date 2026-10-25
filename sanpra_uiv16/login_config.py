"""Public login page configuration: Login Page Settings merged with the site's branding."""

import frappe
from frappe.utils import cint

from sanpra_uiv16 import theme_engine

DOCTYPE = "Login Page Settings"
BRANDING_FIELDS = ("company_name", "logo", "favicon", "brand_color", "accent_color")
LAYOUTS = {"Split Screen": "split", "Centered Card": "centered"}
MAX_FEATURE_CARDS = 4
DEFAULT_FEATURE_ICON = "es-line-tiles"


def public_url(value):
    """clean_url for the guest-facing page: a /private/ file 403s for guests."""
    value = theme_engine.clean_url(value)
    return "" if value.startswith("/private/") else value


# ── 1. BRANDING SOURCES ────────────────────────────────────────────────────────
GENERIC_NAMES = {"frappe", "frappe framework", "erpnext", "frappe erpnext"}


def theme_config():
    try:
        return theme_engine.resolve_config(frappe.get_cached_doc("Theme Settings"))
    except Exception:
        frappe.log_error("sanpra_uiv16.login_config: Theme Settings unavailable")
        return dict(theme_engine.DEFAULT_CONFIG)


def real_name(value):
    value = str(value or "").strip()
    return "" if value.lower() in GENERIC_NAMES else value


def default_company():
    try:
        return frappe.defaults.get_global_default("company") or ""
    except Exception:
        return ""


def company_logo(company):
    if not company:
        return ""
    try:
        if not frappe.db.has_column("Company", "company_logo"):
            return ""
        return public_url(frappe.get_cached_value("Company", company, "company_logo"))
    except Exception:
        return ""


def site_logo():
    """Admin-set Website/Navbar logo only, never an app's hook logo."""
    return public_url(frappe.get_website_settings("app_logo")) or public_url(
        frappe.db.get_single_value("Navbar Settings", "app_logo")
    )


def site_host():
    site = str(getattr(frappe.local, "site", "") or "")
    return site.split(".")[0].replace("-", " ").title() if site else ""


def branding_sources(config=None):
    """Return the site's existing branding for the auto-filled fields."""
    config = config if config is not None else theme_config()
    company = default_company()
    return {
        "company_name": (
            real_name(config.get("app_title"))
            or real_name(company)
            or real_name(frappe.get_website_settings("app_name"))
            or real_name(frappe.get_system_settings("app_name"))
            or site_host()
            or "Workspace"
        ),
        "logo": public_url(config.get("company_logo")) or company_logo(company) or site_logo() or "",
        "favicon": (
            public_url(config.get("favicon"))
            or public_url(frappe.get_website_settings("favicon"))
        ),
        "brand_color": theme_engine.color(config.get("brand_color"), theme_engine.DEFAULT_CONFIG["brand_color"]),
        "accent_color": theme_engine.color(config.get("accent_color"), theme_engine.DEFAULT_CONFIG["accent_color"]),
    }


# ── 1b. BUILT-IN COPY (Edusuccess Education-First) ───────────────────────────
DEFAULT_COPY = {
    "badge_text": "SECURE EDUCATION WORKSPACE",
    "headline": "Smart Education Management in One Unified Platform.",
    "description": "Sign in to Edusuccess to manage admissions, courses, attendance, fees and faculty from one secure workspace.",
    "feature_panel_title": "Core operations at a glance",
    "feature_status_text": "256-bit encrypted",
    "card_eyebrow": "SECURE SIGN-IN",
    "card_heading": "Welcome back",
    "card_subtitle": "Sign in to your Edusuccess account to continue.",
    "button_label": "Sign in",
    "security_note": "Your connection is encrypted. Access permissions comply with personal data protection regulations.",
    "back_link_label": "Back",
}
COPY_FIELDS = tuple(DEFAULT_COPY)

DEFAULT_FEATURES_BUSINESS = (
    ("es-line-people", "Admissions & Students", "Student admissions, class placement & enrollment"),
    ("es-line-plans", "Training & Attendance", "30s dynamic QR attendance, schedules & online learning"),
    ("es-line-reports", "Finance & Tuition Fees", "Automated fee matching, invoices & GL ledger"),
)
DEFAULT_FEATURES_GENERAL = (
    ("es-line-plans", "Organised work", "Records, tasks and approvals"),
    ("es-line-people", "Team collaboration", "Share, assign and comment"),
    ("es-line-reports", "Reports & insights", "Live dashboards and reports"),
)

# ── 1c. HIGH-FIDELITY TRANSLATION MAPS ─────────────────────────────────────────
VI_TRANSLATIONS = {
    # Hero panel
    "Secure education workspace": "HỆ THỐNG QUẢN TRỊ GIÁO DỤC TOÀN DIỆN",
    "SECURE EDUCATION WORKSPACE": "HỆ THỐNG QUẢN TRỊ GIÁO DỤC TOÀN DIỆN",
    "Secure business workspace": "HỆ THỐNG QUẢN TRỊ GIÁO DỤC TOÀN DIỆN",
    "Smart Education Management in One Unified Platform.": "Hệ Thống Quản Trị Giáo Dục Toàn Diện — Edusuccess",
    "Everything your center runs on, in one unified platform.": "Mọi nghiệp vụ trung tâm giáo dục, hội tụ trên một nền tảng.",
    "Everything your business runs on, in one place.": "Mọi nghiệp vụ trung tâm giáo dục, hội tụ trên một nền tảng.",
    "Sign in to Edusuccess to manage admissions, courses, attendance, fees and faculty from one secure workspace.": "Đăng nhập vào Hệ thống Edusuccess để quản lý đào tạo, tuyển sinh, điểm danh QR 30s, học phí VietQR và kết nối học viên trên không gian số bảo mật.",
    "Sign in to {company} to manage admissions, courses, attendance, fees and faculty from one secure workspace.": "Đăng nhập vào Hệ thống Edusuccess để quản lý đào tạo, tuyển sinh, điểm danh QR 30s, học phí VietQR và kết nối học viên trên không gian số bảo mật.",
    "Sign in to {company} to manage your customers, operations, finances and team from one secure workspace.": "Đăng nhập vào Hệ thống Edusuccess để quản lý đào tạo, tuyển sinh, tài chính học phí và kết nối giảng viên - học viên trên không gian làm việc số an toàn.",
    "Core operations at a glance": "Nghiệp vụ trung tâm cốt lõi",
    "Core Operations": "Nghiệp vụ trung tâm cốt lõi",
    "Your workspace at a glance": "Nghiệp vụ trung tâm cốt lõi",
    "256-bit encrypted": "Mã hóa bảo mật 256-bit",
    "256-bit Encrypted": "Mã hóa bảo mật 256-bit",
    "Encrypted connection": "Mã hóa bảo mật 256-bit",

    # Feature cards (supports education keys & legacy keys)
    "Admissions & Students": "Tuyển sinh & Học viên",
    "Sales & customers": "Tuyển sinh & Học viên",
    "Student admissions, class placement & enrollment": "Tiếp nhận học viên, phân lớp & học phí",
    "CRM leads, class placement & enrollment": "Tiếp nhận Lead CRM, xếp lớp & học phí",
    "Quotes, orders and invoices": "Tiếp nhận Lead CRM, xếp lớp & học phí",
    "Training & Attendance": "Đào tạo & Chuyên cần",
    "Operations": "Đào tạo & Chuyên cần",
    "30s dynamic QR attendance, schedules & online learning": "Điểm danh QR 30 giây, thời khóa biểu & học trực tuyến",
    "30s dynamic QR, schedule & LMS online": "Điểm danh QR 30s, thời khóa biểu & LMS",
    "Stock, purchasing and projects": "Điểm danh QR 30s, thời khóa biểu & LMS",
    "Finance & Tuition Fees": "Tài chính & Thu phí VietQR",
    "Finance & VietQR Fees": "Tài chính & Thu phí VietQR",
    "Finance & people": "Tài chính & Thu phí VietQR",
    "Automated fee matching, invoices & GL ledger": "Đối soát VietQR tức thì, hóa đơn & sổ cái",
    "Automated fee reconciliation, invoices & GL ledger": "Đối soát VietQR tức thì, hóa đơn & sổ cái",
    "VietQR matching, tuition fees & GL ledger": "Đối soát VietQR tức thì, hóa đơn & sổ cái",
    "Accounts, reports and your team": "Đối soát VietQR tức thì, hóa đơn & sổ cái",

    # Sign-in card
    "SECURE SIGN-IN": "ĐĂNG NHẬP BẢO MẬT",
    "Secure sign-in": "ĐĂNG NHẬP BẢO MẬT",
    "Welcome back": "Chào mừng bạn trở lại",
    "Sign in to your Edusuccess account to continue.": "Đăng nhập vào tài khoản Edusuccess của bạn để tiếp tục.",
    "Sign in to your {company} account to continue.": "Đăng nhập vào tài khoản Edusuccess của bạn để tiếp tục.",
    "Sign in": "Đăng nhập",
    "Password": "Mật khẩu",
    "Forgot password?": "Quên mật khẩu?",
    "Email or Username": "Email hoặc Tên đăng nhập",
    "Email": "Email",
    "jane@example.com": "nhap.email@edusuccess.vn",
    "enter.email@edusuccess.vn": "nhap.email@edusuccess.vn",
    "Login with Email Link": "Đăng nhập bằng Liên kết Email",
    "Login with password": "Đăng nhập bằng Mật khẩu",
    "Back to sign in": "Quay lại đăng nhập",
    "Back": "Quay lại",
    "Your connection is encrypted. What you can see depends on your assigned role.": "Kết nối được mã hóa bảo mật 256-bit. Quyền truy cập tuân thủ phân quyền và Luật Bảo vệ dữ liệu cá nhân.",
    "Your connection is encrypted. Access permissions comply with personal data protection regulations.": "Kết nối được mã hóa bảo mật 256-bit. Quyền truy cập tuân thủ phân quyền và Luật Bảo vệ dữ liệu cá nhân.",
    "Powered by Sanpra Softwares": "© 2026 Edusuccess • Hệ thống Quản trị Giáo dục & Đào tạo Toàn diện",
    "© 2026 Edusuccess. Hệ thống Quản trị Giáo dục & Đào tạo Toàn diện.": "© 2026 Edusuccess • Hệ thống Quản trị Giáo dục & Đào tạo Toàn diện",
    "© 2026 Edusuccess • Hệ thống Quản trị Giáo dục & Đào tạo Toàn diện": "© 2026 Edusuccess • Hệ thống Quản trị Giáo dục & Đào tạo Toàn diện",
    "© 2026 Edusuccess. Comprehensive Education Management System.": "© 2026 Edusuccess • Hệ thống Quản trị Giáo dục & Đào tạo Toàn diện",
}

EN_TRANSLATIONS = {
    # Hero panel
    "Secure education workspace": "SECURE EDUCATION WORKSPACE",
    "SECURE EDUCATION WORKSPACE": "SECURE EDUCATION WORKSPACE",
    "Secure business workspace": "SECURE EDUCATION WORKSPACE",
    "HỆ THỐNG QUẢN TRỊ GIÁO DỤC TOÀN DIỆN": "SECURE EDUCATION WORKSPACE",
    "Smart Education Management in One Unified Platform.": "Smart Education Management in One Unified Platform.",
    "Hệ Thống Quản Trị Giáo Dục Toàn Diện — Edusuccess": "Smart Education Management in One Unified Platform.",
    "Everything your center runs on, in one unified platform.": "Everything your center runs on, in one unified platform.",
    "Everything your business runs on, in one place.": "Everything your center runs on, in one unified platform.",
    "Mọi nghiệp vụ trung tâm giáo dục, hội tụ trên một nền tảng.": "Everything your center runs on, in one unified platform.",
    "Sign in to Edusuccess to manage admissions, courses, attendance, fees and faculty from one secure workspace.": "Sign in to Edusuccess to manage admissions, courses, attendance, fees and faculty from one secure workspace.",
    "Sign in to {company} to manage admissions, courses, attendance, fees and faculty from one secure workspace.": "Sign in to Edusuccess to manage admissions, courses, attendance, fees and faculty from one secure workspace.",
    "Sign in to {company} to manage your customers, operations, finances and team from one secure workspace.": "Sign in to Edusuccess to manage admissions, courses, attendance, fees and faculty from one secure workspace.",
    "Đăng nhập vào Hệ thống Edusuccess để quản lý đào tạo, tuyển sinh, điểm danh QR 30s, học phí VietQR và kết nối học viên trên không gian số bảo mật.": "Sign in to Edusuccess to manage admissions, courses, attendance, fees and faculty from one secure workspace.",
    "Đăng nhập vào Hệ thống Edusuccess để quản lý đào tạo, tuyển sinh, tài chính học phí và kết nối giảng viên - học viên trên không gian làm việc số an toàn.": "Sign in to Edusuccess to manage admissions, courses, attendance, fees and faculty from one secure workspace.",
    "Core operations at a glance": "Core Operations",
    "Core Operations": "Core Operations",
    "Your workspace at a glance": "Core Operations",
    "Nghiệp vụ trung tâm cốt lõi": "Core Operations",
    "256-bit encrypted": "256-bit Encrypted",
    "256-bit Encrypted": "256-bit Encrypted",
    "Encrypted connection": "256-bit Encrypted",
    "Mã hóa bảo mật 256-bit": "256-bit Encrypted",

    # Feature cards
    "Admissions & Students": "Admissions & Students",
    "Tuyển sinh & Học viên": "Admissions & Students",
    "Sales & customers": "Admissions & Students",
    "Student admissions, class placement & enrollment": "Student admissions, class placement & enrollment",
    "CRM leads, class placement & enrollment": "Student admissions, class placement & enrollment",
    "Quotes, orders and invoices": "Student admissions, class placement & enrollment",
    "Tiếp nhận học viên, phân lớp & học phí": "Student admissions, class placement & enrollment",
    "Tiếp nhận Lead CRM, xếp lớp & học phí": "Student admissions, class placement & enrollment",
    "Training & Attendance": "Training & Attendance",
    "Đào tạo & Chuyên cần": "Training & Attendance",
    "Operations": "Training & Attendance",
    "30s dynamic QR attendance, schedules & online learning": "30s dynamic QR attendance, schedules & online learning",
    "30s dynamic QR, schedule & LMS online": "30s dynamic QR attendance, schedules & online learning",
    "Stock, purchasing and projects": "30s dynamic QR attendance, schedules & online learning",
    "Điểm danh QR 30 giây, thời khóa biểu & học trực tuyến": "30s dynamic QR attendance, schedules & online learning",
    "Điểm danh QR 30s, thời khóa biểu & LMS": "30s dynamic QR attendance, schedules & online learning",
    "Finance & Tuition Fees": "Finance & Tuition Fees",
    "Finance & VietQR Fees": "Finance & Tuition Fees",
    "Tài chính & Thu phí VietQR": "Finance & Tuition Fees",
    "Finance & people": "Finance & Tuition Fees",
    "Automated fee matching, invoices & GL ledger": "Automated fee matching, invoices & GL ledger",
    "Automated fee reconciliation, invoices & GL ledger": "Automated fee matching, invoices & GL ledger",
    "VietQR matching, tuition fees & GL ledger": "Automated fee matching, invoices & GL ledger",
    "Đối soát VietQR tức thì, hóa đơn & sổ cái": "Automated fee matching, invoices & GL ledger",
    "Accounts, reports and your team": "Automated fee matching, invoices & GL ledger",

    # Sign-in card
    "SECURE SIGN-IN": "SECURE SIGN-IN",
    "Secure sign-in": "SECURE SIGN-IN",
    "ĐĂNG NHẬP BẢO MẬT": "SECURE SIGN-IN",
    "Welcome back": "Welcome back",
    "Chào mừng bạn trở lại": "Welcome back",
    "Sign in to your Edusuccess account to continue.": "Sign in to your Edusuccess account to continue.",
    "Sign in to your {company} account to continue.": "Sign in to your Edusuccess account to continue.",
    "Đăng nhập vào tài khoản Edusuccess của bạn để tiếp tục.": "Sign in to your Edusuccess account to continue.",
    "Sign in": "Sign in",
    "Đăng nhập": "Sign in",
    "Password": "Password",
    "Mật khẩu": "Password",
    "Forgot password?": "Forgot password?",
    "Quên mật khẩu?": "Forgot password?",
    "Email or Username": "Email or Username",
    "Email": "Email",
    "Email hoặc Tên đăng nhập": "Email or Username",
    "jane@example.com": "enter.email@edusuccess.vn",
    "nhap.email@edusuccess.vn": "enter.email@edusuccess.vn",
    "enter.email@edusuccess.vn": "enter.email@edusuccess.vn",
    "Login with Email Link": "Login with Email Link",
    "Đăng nhập bằng Liên kết Email": "Login with Email Link",
    "Đăng nhập bằng liên kết Email": "Login with Email Link",
    "Login with password": "Login with Password",
    "Đăng nhập bằng Mật khẩu": "Login with Password",
    "Đăng nhập bằng mật khẩu": "Login with Password",
    "Back to sign in": "Back to sign in",
    "Quay lại đăng nhập": "Back to sign in",
    "Back": "Back",
    "Quay lại": "Back",
    "Your connection is encrypted. What you can see depends on your assigned role.": "Your connection is encrypted. Access permissions comply with personal data protection regulations.",
    "Your connection is encrypted. Access permissions comply with personal data protection regulations.": "Your connection is encrypted. Access permissions comply with personal data protection regulations.",
    "Kết nối được mã hóa bảo mật 256-bit. Quyền truy cập tuân thủ phân quyền và Luật Bảo vệ dữ liệu cá nhân.": "Your connection is encrypted. Access permissions comply with personal data protection regulations.",
    "Powered by Sanpra Softwares": "© 2026 Edusuccess. Comprehensive Education Management System.",
    "© 2026 Edusuccess. Hệ thống Quản trị Giáo dục & Đào tạo Toàn diện.": "© 2026 Edusuccess. Comprehensive Education Management System.",
    "© 2026 Edusuccess • Hệ thống Quản trị Giáo dục & Đào tạo Toàn diện": "© 2026 Edusuccess. Comprehensive Education Management System.",
    "© 2026 Edusuccess. Comprehensive Education Management System.": "© 2026 Edusuccess. Comprehensive Education Management System.",
}


def default_features():
    try:
        business = "erpnext" in frappe.get_installed_apps()
    except Exception:
        business = False
    rows = DEFAULT_FEATURES_BUSINESS if business else DEFAULT_FEATURES_GENERAL
    return [frappe._dict(icon=icon, title=title, subtitle=subtitle) for icon, title, subtitle in rows]


# ── 2. MERGED PAGE CONFIG ──────────────────────────────────────────────────────
def safe_link(value):
    """Allow same-site paths and absolute http(s) URLs only."""
    value = str(value or "").strip()
    if value.startswith("/") and not value.startswith("//"):
        return value[:500]
    return value[:500] if value.startswith(("https://", "http://")) else ""


def initials(name):
    words = str(name or "").split()
    return "".join(word[0] for word in words[:2]).upper() or "E"


def normalize_brand_name(name, lang="vi"):
    raw = str(name or "").strip()
    if not raw or any(kw in raw.upper() for kw in ("CÔNG TY", "TNHH", "SUCCESS", "EDUSUCCESS", "WORKSPACE")):
        return "Edusuccess"
    return raw


def text_of(value, company):
    """Translate stored copy with high-fidelity dictionary fallback,
    ensuring 100% pure Vietnamese when lang=vi and 100% pure English when lang=en."""
    value = str(value or "").strip()
    if not value:
        return ""

    current_lang = getattr(frappe.local, "lang", "vi")

    # Normalize any Vietnamese legal company entity string embedded in value back to {company}
    for raw_legal in (
        "CÔNG TY TNHH ĐẦU TƯ PHÁT TRIỂN GIÁO DỤC QUỐC TẾ SUCCESS",
        company,
    ):
        if raw_legal and raw_legal in value:
            value = value.replace(raw_legal, "{company}")

    if current_lang == "vi":
        if value in VI_TRANSLATIONS:
            res = VI_TRANSLATIONS[value]
        else:
            res = frappe._(value)
    else:
        if value in EN_TRANSLATIONS:
            res = EN_TRANSLATIONS[value]
        else:
            res = frappe._(value, lang="en") if hasattr(frappe, "_") else value

    # Guarantee NO Vietnamese legal company entity string or placeholder leaks into final output
    res = res.replace("CÔNG TY TNHH ĐẦU TƯ PHÁT TRIỂN GIÁO DỤC QUỐC TẾ SUCCESS", "Edusuccess")
    if "{company}" in res:
        res = res.replace("{company}", "Edusuccess")

    return res.strip()


def theme_copy(config, key):
    """Theme Studio login text, but only once an admin has changed it."""
    value = str(config.get(key) or "").strip()
    return "" if value == theme_engine.DEFAULT_CONFIG.get(key) else value


def get_settings_doc():
    try:
        return frappe.get_cached_doc(DOCTYPE)
    except Exception:
        # Doctype not migrated yet: behave as if the designer is switched off.
        return None


def resolve_request_language():
    """Resolve Guest/User language for login: URL ?lang= > explicit cookie preferred_language > 'vi'"""
    try:
        req = getattr(frappe, "request", None)
        args = getattr(frappe, "form_dict", {}) or {}
        # 1. URL parameter ?lang= has highest priority
        lang = (args.get("lang") or "").strip().lower()
        if not lang and req:
            # 2. Check explicit preferred_language cookie (set when user explicitly clicked switcher)
            cookies = getattr(req, "cookies", {}) or {}
            lang = (cookies.get("preferred_language") or "").strip().lower()
        # 3. Always default to "vi" for Edusuccess Vietnam
        if lang not in ("vi", "en"):
            lang = "vi"

        frappe.local.lang = lang
        frappe.local.lang_full_dict = None
        return lang
    except Exception:
        frappe.local.lang = "vi"
        return "vi"


def get_login_config():
    """Everything the login template needs, with branding fallbacks resolved."""
    # ── Resolve Guest Language (Default VI for Edusuccess, toggleable to EN) ──
    resolve_request_language()

    config = theme_config()
    brand = branding_sources(config)
    doc = get_settings_doc()
    if not doc:
        return frappe._dict(enabled=False, layout="centered", **brand, preferred_mode=config.get("preferred_mode"))

    auto = cint(doc.auto_fetch_branding)

    def pick(field):
        return brand[field] if auto else (doc.get(field) or brand[field])

    company = normalize_brand_name(pick("company_name"), getattr(frappe.local, "lang", "vi"))

    def text(field, fallback=""):
        return text_of(doc.get(field) or fallback or DEFAULT_COPY.get(field, ""), company)

    rows = [row for row in (doc.feature_cards or []) if row.title] or default_features()

    features = [
        {
            "icon": row.icon or DEFAULT_FEATURE_ICON,
            "title": text_of(row.title, company),
            "subtitle": text_of(row.subtitle, company),
        }
        for row in rows[:MAX_FEATURE_CARDS]
    ]

    # Resolve elegant default footer text aligned with current language
    current_lang = getattr(frappe.local, "lang", "vi")
    if current_lang == "en":
        default_footer = "© 2026 Edusuccess. Comprehensive Education Management System."
    else:
        default_footer = "© 2026 Edusuccess • Hệ thống Quản trị Giáo dục & Đào tạo Toàn diện"
    footer_text = config.get("footer_text") or default_footer
    if "Sanpra" in footer_text or "CÔNG TY" in footer_text:
        footer_text = default_footer

    return frappe._dict(
        enabled=bool(cint(doc.enabled)),
        layout=LAYOUTS.get(doc.layout, "split"),
        # Branding
        company_name=company,
        initials=initials(company),
        logo=public_url(pick("logo")) or brand["logo"],
        hero_logo=public_url(doc.hero_logo) or public_url(pick("logo")) or brand["logo"],
        favicon=public_url(pick("favicon")) or brand["favicon"],
        brand_color=theme_engine.color(pick("brand_color"), brand["brand_color"]),
        accent_color=theme_engine.color(pick("accent_color"), brand["accent_color"]),
        # Readable text on the hero/button gradient, which starts at this color.
        on_hero=theme_engine.contrast_text(
            theme_engine.color(doc.hero_gradient_from) or theme_engine.color(pick("brand_color"), brand["brand_color"])
        ),
        # Hero panel
        badge_text=text("badge_text"),
        headline=text("headline"),
        description=text("description"),
        hero_bg_image=public_url(doc.hero_bg_image),
        hero_from=theme_engine.color(doc.hero_gradient_from),
        hero_to=theme_engine.color(doc.hero_gradient_to),
        show_pattern=bool(cint(doc.show_hero_pattern)),
        show_feature_panel=bool(cint(doc.show_feature_panel)) and bool(features),
        feature_panel_title=text("feature_panel_title"),
        feature_status_text=text("feature_status_text"),
        features=features,
        # Sign-in card
        card_eyebrow=text("card_eyebrow"),
        card_heading=text("card_heading", theme_copy(config, "login_heading")),
        card_subtitle=text("card_subtitle", theme_copy(config, "login_description")),
        button_label=text("button_label"),
        security_note=text("security_note"),
        back_link_label=text("back_link_label"),
        back_link_url=safe_link(doc.back_link_url),
        # Carried over from Theme Studio
        preferred_mode=config.get("preferred_mode") or "Light",
        footer_text=footer_text,
        hide_powered=True,  # Fully eliminate vendor "Powered by Sanpra Softwares"
    )
