/**
 * smart_home_ops.test.js — widget "Giám sát vận hành" KHÔNG được gọi
 * `scope:"site"` vô điều kiện.
 *
 * Vì sao test này tồn tại: `_refresh_ops()` gọi
 * `smart_edu_core.api.ops.get_ops_summary` với `scope:"site"` cho **mọi** user.
 * Người không có viewer role nhận 403 ⇒ Frappe bắn toast "Không được phép" mỗi
 * lần mở `/desk` (đo staging 12/11/2026 — PermissionError tại
 * `api/dashboard.py:195`). Fix: gọi `scope:"me"` trước, đọc cờ `site_allowed`
 * do server trả, chỉ gọi `scope:"site"` khi cờ là true.
 *
 * Test chạy **code JS thật** trong `node:vm` (không grep chuỗi) nên bắt được
 * cả lỗi "gọi site trước khi biết quyền" lẫn lỗi "gọi site khi không có quyền".
 *
 * Chạy: `node --test tests/*.test.js`
 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const PAGE_JS = path.join(
	__dirname,
	"..",
	"sanpra_uiv16",
	"sanpra_ui_v16",
	"page",
	"smart_home",
	"smart_home.js"
);

/** Element giả — đủ API mà `_refresh_ops` dùng (html/prop/text/length). */
function fakeElement() {
	return {
		length: 1,
		html() {
			return this;
		},
		prop() {
			return this;
		},
		text() {
			return this;
		},
	};
}

/**
 * Nạp `smart_home.js` thật vào context riêng, trả về lớp `SmartHome` + danh sách
 * lệnh gọi `frappe.xcall` đã ghi lại.
 */
function loadSmartHome(meResponse) {
	const calls = [];
	let ctx = null;

	const frappeStub = {
		provide(name) {
			ctx[name] = ctx[name] || {};
		},
		pages: { "smart-home": {} },
		session: { user: "teacher@example.com" },
		ui: { make_app_page() {} },
		xcall(method, args) {
			calls.push({ method, args });
			const payload = Object.assign({}, meResponse || {});
			if (args && args.scope === "site") {
				payload.scope = "site";
				payload.errors_24h = 4;
				payload.jobs_failed_24h = 1;
				payload.job_status_summary = { ran: 1, stale: 0, never_ran: 0, stopped: 0 };
				payload.groups = [];
			}
			return Promise.resolve(payload);
		},
	};

	ctx = {
		console,
		frappe: frappeStub,
		__: (s) => s,
		$: () => ({ find: () => fakeElement() }),
		Promise,
		setTimeout,
		clearTimeout,
	};
	ctx.window = ctx;

	vm.createContext(ctx);
	vm.runInContext(fs.readFileSync(PAGE_JS, "utf8"), ctx);

	return { SmartHome: ctx.sanpra_uiv16.SmartHome, calls };
}

/** Chạy `_refresh_ops()` với response `scope:"me"` cho sẵn rồi trả lệnh gọi đã ghi. */
async function refreshOps(meResponse) {
	const { SmartHome, calls } = loadSmartHome(meResponse);
	const instance = Object.create(SmartHome.prototype);
	instance.$body = { find: () => fakeElement() };

	instance._refresh_ops();
	// Chờ cả 2 vòng promise (me -> site) rút xong.
	await new Promise((resolve) => setImmediate(resolve));
	await new Promise((resolve) => setImmediate(resolve));

	return calls;
}

function scopesOf(calls) {
	return calls.map((call) => call.args && call.args.scope);
}

test("user khong co quyen thi KHONG duoc goi scope site", async () => {
	const calls = await refreshOps({ scope: "me", site_allowed: false, todos_open: 3 });

	assert.deepEqual(scopesOf(calls), ["me"], "phai goi dung 1 lan scope=me, khong goi scope=site");
});

test("viewer duoc goi scope site sau khi da biet quyen", async () => {
	const calls = await refreshOps({ scope: "me", site_allowed: true, todos_open: 3 });

	assert.deepEqual(scopesOf(calls), ["me", "site"], "viewer goi me truoc, site sau");
});

test("response chua co site_allowed (ERP chua deploy) thi fail-safe: khong goi scope site", async () => {
	const calls = await refreshOps({ scope: "me", todos_open: 3 });

	assert.deepEqual(scopesOf(calls), ["me"], "khong co co site_allowed thi KHONG goi scope site");
});

test("moi lệnh gọi đều trúng đúng method", async () => {
	const calls = await refreshOps({ scope: "me", site_allowed: true });

	for (const call of calls) {
		assert.equal(call.method, "smart_edu_core.api.ops.get_ops_summary");
	}
});
