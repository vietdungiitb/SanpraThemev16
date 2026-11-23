/* ================================================================
   Sanpra UI V16 — Canonical workspace route
   Dùng chung cho mọi chỗ sinh href workspace trên Desk.

   Vì sao cần: 4 chỗ từng làm `page.route || slug(name)`. Khi payload
   mang một `route` dùng chung (vd /desk/accounts/accounting cho cả
   Invoicing/Payments/Financial Reports), cả 4 phát cùng một href ⇒
   user bấm mục nào cũng về Accounting. Route chỉ được tin khi nó
   trỏ đúng chính workspace đang xét (assert bằng name/title — nguồn
   sự thật), không phải hằng số do code khác tự gán.
   ================================================================ */
(function () {
  "use strict";

  function slug(value) {
    if (frappe.router && typeof frappe.router.slug === "function") {
      return frappe.router.slug(value);
    }
    return String(value || "")
      .toLowerCase()
      .replace(/ /g, "-");
  }

  /**
   * Trả route (không có tiền tố /desk/) của đúng workspace `page`.
   * Trả "" khi không suy được danh tính — caller PHẢI bỏ qua item đó,
   * không được phát href="/desk/".
   */
  function canonicalWorkspaceRoute(page) {
    if (!page || typeof page !== "object") return "";

    var own = slug(page.name || page.title || "");
    if (!own) return "";

    var raw = page.route ? String(page.route) : "";
    if (raw.indexOf("/desk/") === 0) raw = raw.slice("/desk/".length);
    if (raw.charAt(0) === "/") raw = raw.slice(1);
    if (!raw) return own;

    // Chỉ giữ route khi nó kết thúc bằng đúng slug của chính page này.
    if (raw === own || raw.lastIndexOf("/" + own) === raw.length - own.length - 1) {
      return raw;
    }
    return own;
  }

  frappe.provide("sanpra_uiv16");
  sanpra_uiv16.canonicalWorkspaceRoute = canonicalWorkspaceRoute;
}());
