/**
 * Fail-before test cho bug: 3 workspace con cua module Accounts deu tra ve cung 1 href.
 *
 * Chay: node --test tests/workspace_route.test.js
 *
 * Test doc code JS THAT trong node:vm (khong grep chuoi don gian):
 *  - static guard: regex DA DONG de bat pattern `route || slug(...)` o 4 call-site.
 *  - command_palette: nap file that, cap stale route cho 3 workspace, goi action()
 *    va assert 3 route khac nhau.
 *  - module_cards.buildCard: nap file that, assert href suy tu `name`.
 *  - canonicalWorkspaceRoute (sau fix): helpers suy tu `name/title`, khong tin route lech.
 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const ROOT = path.join(__dirname, "..");
const JS = path.join(ROOT, "sanpra_uiv16", "public", "js");

const STALE = "/desk/accounts/accounting";
const PAGES = [
	{ name: "Invoicing", title: "Lap hoa don", route: STALE, public: 1 },
	{ name: "Payments", title: "Cac thanh toan", route: STALE, public: 1 },
	{ name: "Financial Reports", title: "Bao cao tai chinh", route: STALE, public: 1 },
];

function baseFrappe(ctx) {
	const routes = [];
	const frappe = {
		boot: {
			user: { can_read: [], can_create: [] },
			allowed_reports: {},
			sidebar_items: { pages: PAGES },
		},
		router: {
			slug(value) {
				return String(value || "")
					.toLowerCase()
					.replace(/ /g, "-");
			},
		},
		utils: {
			escape_html(value) {
				return String(value);
			},
		},
		set_route(route) {
			routes.push(route);
		},
		provide(name) {
			ctx[name] = ctx[name] || {};
		},
	};
	return { frappe, routes };
}

function makeContext(extra = {}) {
	const ctx = {
		console: { warn() {}, log() {}, error() {} },
		window: {},
		document: {
			readyState: "complete",
			addEventListener() {},
		},
		setTimeout() {},
		setInterval() {},
		clearInterval() {},
		__: (s) => s,
	};
	ctx.$ = function () {
		return {
			ready() {},
			on() {},
			off() {},
			find() {
				return this;
			},
			length: 0,
		};
	};
	ctx.window.document = ctx.document;
	Object.assign(ctx, extra);
	// Trong trinh duyet window === globalThis; dat bang nhau de code goi
	// `sanpra_uiv16.canonicalWorkspaceRoute` khong can stub them.
	ctx.window = ctx;
	ctx.globalThis = ctx;
	vm.createContext(ctx);
	return ctx;
}

function load(file, ctx) {
	// hooks.py nap workspace_route.js TRUOC cac file tieu thu no.
	// Khi chay tren baseline (chua co helper) thi BO QUA — test phai do
	// vi logic sai, khong phai vi ENOENT / Cannot find module.
	if (file !== "workspace_route.js" && !ctx._helperLoaded) {
		const helperPath = path.join(JS, "workspace_route.js");
		if (fs.existsSync(helperPath)) {
			vm.runInContext(fs.readFileSync(helperPath, "utf8"), ctx, {
				filename: "workspace_route.js",
			});
		}
		ctx._helperLoaded = true;
	}
	const code = fs.readFileSync(path.join(JS, file), "utf8");
	vm.runInContext(code, ctx, { filename: file });
}

function hrefOf(html) {
	const m = String(html).match(/href="([^"]*)"/);
	return m ? m[1] : null;
}

test("AC-5 static guard: khong con pattern route || slug o 4 call-site", () => {
	// Regex DA DONG: command_palette co `page.route` o dong 80 va `slug` o dong 81.
	const pattern = /\broute\s*\|\|[\s\S]{0,200}?\bslug(?:ify)?\s*\(/g;
	const files = ["sanpra_uiv16.js", "command_palette.js", "module_cards.js"];
	const hits = [];
	for (const file of files) {
		const src = fs.readFileSync(path.join(JS, file), "utf8");
		for (const m of src.matchAll(pattern)) {
			const line = src.slice(0, m.index).split("\n").length;
			hits.push(`${file}:${line}`);
		}
	}
	assert.deepEqual(
		hits,
		[],
		`Con ${hits.length} call-site dung route || slug (co the dung chung route stale): ${hits.join(", ")}`
	);
});

test("AC-1 command_palette: 3 workspace cung stale route phai cho 3 route khac nhau", () => {
	const ctx = makeContext();
	const { frappe, routes } = baseFrappe(ctx);
	ctx.frappe = frappe;
	ctx.window.frappe = frappe;
	load("command_palette.js", ctx);

	const cp = ctx.window.sanpra_uiv16.cp;
	assert.ok(cp, "command palette khong khoi tao");
	cp._build_items();
	const workspaces = cp.all_items.filter((i) => i.type === "workspace");
	assert.equal(workspaces.length, 3, "phai co 3 workspace trong fixture");
	workspaces.forEach((item) => item.action());

	const urls = routes.map((r) => (r.indexOf("/desk/") === 0 ? r : "/desk/" + r));
	assert.deepEqual(
		Array.from(new Set(urls)),
		["/desk/invoicing", "/desk/payments", "/desk/financial-reports"],
		`3 workspace bi gop ve cung route: ${JSON.stringify(routes)}`
	);
});

test("AC-1 regression module_cards.buildCard: href suy tu name, khong dung route stale", () => {
	const ctx = makeContext();
	const { frappe } = baseFrappe(ctx);
	ctx.frappe = frappe;
	ctx.window.frappe = frappe;
	load("module_cards.js", ctx);

	const cards = ctx.sanpra_uiv16.workspaceCards;
	assert.ok(cards && typeof cards.buildCard === "function", "khong tim thay buildCard");
	const hrefs = PAGES.map((p, i) => hrefOf(cards.buildCard(p, i)));
	assert.deepEqual(hrefs, [
		"/desk/invoicing",
		"/desk/payments",
		"/desk/financial-reports",
	]);
});

test("AC-1..3 canonicalWorkspaceRoute: tin route cua chinh no, loai route lech", () => {
	const file = path.join(JS, "workspace_route.js");
	assert.ok(fs.existsSync(file), "Thieu workspace_route.js (helper chua duoc them)");
	const ctx = makeContext();
	const { frappe } = baseFrappe(ctx);
	ctx.frappe = frappe;
	ctx.window.frappe = frappe;
	load("workspace_route.js", ctx);
	const fn = ctx.sanpra_uiv16.canonicalWorkspaceRoute;
	assert.equal(typeof fn, "function", "khong tim thay canonicalWorkspaceRoute");

	// AC-1: route lech bi loai
	assert.equal(fn(PAGES[0]), "invoicing");
	// AC-2: route dung cua chinh no duoc giu (co shell prefix)
	assert.equal(fn({ name: "Invoicing", route: "/desk/accounts/invoicing" }), "accounts/invoicing");
	// AC-3: khong co name/title -> rong, caller se skip
	assert.equal(fn({ route: STALE }), "");
	assert.equal(fn({ title: "Bao cao tai chinh", route: STALE }), "bao-cao-tai-chinh");
});
