/* ================================================================
   Sanpra UI V16 — Smart Home / Today's View
   Permission-aware widgets with a persistent drag-and-drop layout.
   ================================================================ */

frappe.provide("sanpra_uiv16");

/* ────────────────────────────────────────────────────────────────────────────
   1. FRAPPE PAGE LIFECYCLE
   Build once on page load; SPA revisits only refresh live values so the user's
   widget order and the existing DOM remain intact.
   ──────────────────────────────────────────────────────────────────────────── */
frappe.pages["smart-home"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Today's View"),
		single_column: true,
	});

	var instance = new sanpra_uiv16.SmartHome(wrapper);
	frappe.pages["smart-home"]._inst = instance;
	instance.build();
};

frappe.pages["smart-home"].on_page_show = function () {
	var instance = frappe.pages["smart-home"]._inst;
	if (instance) instance.refresh();
};

/* ────────────────────────────────────────────────────────────────────────────
   2. DASHBOARD CONTROLLER
   Owns widget rendering, edit state, persistence, permissions, and data refresh.
   ──────────────────────────────────────────────────────────────────────────── */
sanpra_uiv16.SmartHome = class SmartHome {
	constructor(wrapper) {
		this.wrapper = $(wrapper);
		this.$body = this.wrapper.find(".page-content");
		this.user = (frappe.session && frappe.session.user) || "Guest";
		this.storage_key = "st_smart_home_layout_v3::" + this.user;
		this.editing = false;
		this.dragged = null;
		this.library_drag_id = null;
		this._built = false;
		this.kpis = this._get_kpi_definitions();
		this.state = this._load_layout();
	}

	/* Public entry point; guarded because Frappe can revisit a cached page. */
	build() {
		if (this._built) return;
		this._built = true;
		this._build_shell();
		this._render_widgets();
		this._restore_layout();
		this._bind_layout_events();
		this.refresh();
	}

	/* Update data in place without rebuilding or reordering widget nodes. */
	refresh() {
		if (!this._built) return;
		this._refresh_kpis();
		this._refresh_recent();
		this._refresh_pending();
		this._refresh_ops();
		this._refresh_today();
	}

	/* ── 3. PAGE SHELL ────────────────────────────────────────────────────────
	   The greeting is fixed page chrome; everything below it is a widget. */
	_build_shell() {
		var hour = new Date().getHours();
		var greeting =
			hour < 12 ? __("Good morning") :
			hour < 17 ? __("Good afternoon") :
			__("Good evening");

		var user_info = ((frappe.boot && frappe.boot.user_info) || {})[this.user] || {};
		var full_name =
			user_info.full_name ||
			(frappe.session && frappe.session.user_fullname) ||
			this.user ||
			"";
		var date_label = new Date().toLocaleDateString(this._site_locale(), {
			weekday: "long",
			year: "numeric",
			month: "long",
			day: "numeric",
		});

		this.$body.html(
			'<main class="st-smart-home">' +
				'<header class="st-sh-header">' +
					'<div class="st-sh-welcome">' +
						'<div class="st-sh-eyebrow">' + __("Your command centre") + '</div>' +
						'<h2 class="st-sh-greeting">' +
							greeting + ', <span class="st-sh-name">' + this._esc(full_name) + '</span>' +
						'</h2>' +
						'<div class="st-sh-date">' + this._esc(date_label) + '</div>' +
					'</div>' +
					'<div class="st-sh-header-actions">' +
						'<span class="st-sh-save-state" role="status" aria-live="polite"></span>' +
						'<button class="btn btn-default btn-sm st-sh-add-widgets" type="button">' +
							this._icon("add", "sm") + '<span>' + __("Add widgets") + '</span>' +
						'</button>' +
						'<button class="btn btn-default btn-sm st-sh-reset" type="button">' +
							this._icon("refresh", "sm") + '<span>' + __("Reset") + '</span>' +
						'</button>' +
						'<button class="btn btn-primary btn-sm st-sh-customize" type="button" aria-pressed="false">' +
							this._icon("edit", "sm") +
							'<span class="st-sh-customize-label">' + __("Customize layout") + '</span>' +
						'</button>' +
						'<a href="/desk/all-apps" class="st-sh-all-ws">' +
							__("All Workspaces") + ' <span aria-hidden="true">&rarr;</span>' +
						'</a>' +
					'</div>' +
				'</header>' +
				this._widget_library_markup() +
				'<div class="st-sh-edit-note" role="status">' +
					'<span class="st-sh-edit-note-icon">' + this._icon("drag", "sm") + '</span>' +
					'<span>' + __("Drag widgets to rearrange them. Your layout saves automatically.") + '</span>' +
				'</div>' +
				'<div class="st-sh-widget-grid" id="st-sh-widget-grid"></div>' +
			'</main>'
		);
	}

	/* The library is a lightweight drawer: templates can be clicked or dragged. */
	_widget_library_markup() {
		var self = this;
		var templates = this._widget_templates();
		return (
			'<div class="st-sh-library-backdrop" hidden></div>' +
			'<aside class="st-sh-library" aria-hidden="true" aria-label="' + __("Widget library") + '">' +
				'<div class="st-sh-library-head">' +
					'<div><span class="st-sh-library-kicker">' + __("Make it yours") + '</span>' +
					'<h3>' + __("Widget library") + '</h3>' +
					'<p>' + __("Click a widget or drag it onto your dashboard.") + '</p></div>' +
					'<button class="st-sh-library-close" type="button" aria-label="' + __("Close") + '">&times;</button>' +
				'</div>' +
				'<div class="st-sh-library-list">' +
					templates.map(function (item) {
						return (
							'<button class="st-sh-library-item" type="button" draggable="true" data-template-id="' + item.id + '">' +
								'<span class="st-sh-library-icon st-sh-tone-' + item.accent + '">' + self._icon(item.icon, "md") + '</span>' +
								'<span><strong>' + item.title + '</strong><small>' + item.description + '</small></span>' +
								'<span class="st-sh-library-add" aria-hidden="true">+</span>' +
							'</button>'
						);
					}).join("") +
				'</div>' +
				'<button class="st-sh-build-widget" type="button">' +
					'<span class="st-sh-build-plus">+</span><span><strong>' + __("Build your own") + '</strong>' +
					'<small>' + __("Create a note, number or shortcut in seconds") + '</small></span>' +
				'</button>' +
			'</aside>' +
			this._builder_markup()
		);
	}

	_builder_markup() {
		return (
			'<div class="st-sh-builder-backdrop" hidden>' +
				'<section class="st-sh-builder" role="dialog" aria-modal="true" aria-labelledby="st-sh-builder-title">' +
					'<div class="st-sh-builder-head"><div><span>' + __("Simple builder") + '</span>' +
						'<h3 id="st-sh-builder-title">' + __("Create a widget") + '</h3></div>' +
						'<button class="st-sh-builder-close" type="button" aria-label="' + __("Close") + '">&times;</button></div>' +
					'<div class="st-sh-builder-layout"><form class="st-sh-builder-form">' +
						'<label>' + __("Widget type") + '<select name="type">' +
							'<option value="note">' + __("Note") + '</option><option value="number">' + __("Number") + '</option>' +
							'<option value="link">' + __("Shortcut") + '</option></select></label>' +
						'<label>' + __("Title") + '<input name="title" maxlength="48" value="' + __("My widget") + '" required></label>' +
						'<label class="st-sh-builder-value">' + __("Content") + '<textarea name="value" maxlength="240" rows="3" placeholder="' + __("Write something useful...") + '"></textarea></label>' +
						'<label class="st-sh-builder-url" hidden>' + __("Link") + '<input name="url" type="url" placeholder="/desk/todo"></label>' +
						'<div class="st-sh-builder-row"><label>' + __("Size") + '<select name="size"><option value="quarter">' + __("Small") + '</option>' +
							'<option value="half" selected>' + __("Medium") + '</option><option value="wide">' + __("Wide") + '</option></select></label>' +
							'<label>' + __("Colour") + '<select name="accent"><option value="blue">' + __("Blue") + '</option>' +
							'<option value="green">' + __("Green") + '</option><option value="amber">' + __("Amber") + '</option>' +
							'<option value="coral">' + __("Coral") + '</option></select></label></div>' +
						'<button class="btn btn-primary st-sh-builder-submit" type="submit">' + __("Add to dashboard") + '</button>' +
					'</form><div class="st-sh-builder-preview"><span>' + __("Live preview") + '</span><div data-builder-preview></div></div></div>' +
				'</section>' +
			'</div>'
		);
	}

	/* ── 4. WIDGET REGISTRY / FACTORIES ──────────────────────────────────────
	   Permission-safe KPI definitions and standard panels share one grid. */
	_render_widgets() {
		var $grid = this.$body.find("#st-sh-widget-grid");
		var self = this;
		var hidden = this.state.hidden || [];

		/* Layer 1 (personal): personal KPIs come first so the daily routine is
		   visible immediately; system KPIs follow so they stay deliberate. */
		var personal_ids = ["my-todos", "open-tasks"];
		this.kpis
			.slice()
			.sort(function (a, b) {
				return personal_ids.indexOf(b.id) !== -1 ? 1 : -1;
			})
			.forEach(function (kpi) {
				if (hidden.indexOf(kpi.id) === -1) $grid.append(self._kpi_widget(kpi));
			});

		/* Thu tu mac dinh theo muc do uu tien (RICH-ORDER 2026-11-10):
		   bo 3 hanh dong -> giam sat he thong -> tiep tuc viec do/tao moi
		   -> launcher xuong cuoi. */
		if (hidden.indexOf("today-focus") === -1) $grid.append(
			this._panel_widget(
				"today-focus",
				__("My Day"),
				__("Your todos, events and notifications"),
				"calendar",
				"half",
				'<div id="st-sh-today" class="st-sh-card-body"><div class="st-sh-spin"></div></div>'
			)
		);
		if (hidden.indexOf("needs-attention") === -1) $grid.append(
			this._panel_widget(
				"needs-attention",
				__("Needs Attention"),
				__("Items waiting on action"),
				"warning",
				"half",
				'<div id="st-sh-pending" class="st-sh-card-body"><div class="st-sh-spin"></div></div>'
			)
		);
		if (hidden.indexOf("reports-charts") === -1) $grid.append(
			this._panel_widget(
				"reports-charts",
				__("Reports"),
				__("One click to the ops reports"),
				"chart",
				"half",
				'<div id="st-sh-rc" class="st-sh-card-body"></div>'
			)
		);

		/* Layer 3 (system, viewer-only): ops entry, revealed only if the pool
		   let this user see the workspace (same check as header ops icon). */
		if (hidden.indexOf("giam-sat-van-hanh") === -1) $grid.append(this._ops_widget());

		if (hidden.indexOf("recent-documents") === -1) $grid.append(
			this._panel_widget(
				"recent-documents",
				__("Recent Documents"),
				__("Records you opened lately"),
				"clock",
				"wide",
				'<div id="st-sh-recent" class="st-sh-card-body"><div class="st-sh-spin"></div></div>'
			)
		);
		if (hidden.indexOf("quick-create") === -1) $grid.append(
			this._panel_widget(
				"quick-create",
				__("Quick Create"),
				__("Start something new"),
				"add",
				"half",
				'<div id="st-sh-qc" class="st-sh-card-body"></div>'
			)
		);
		/* Launcher xuong cuoi: tan suat dung thap khi da quen route, sidebar da cover. */
		if (hidden.indexOf("your-apps") === -1) $grid.append(this._apps_widget());

		(this.state.added || []).forEach(function (id) {
			var template = self._find_template(id);
			if (template && hidden.indexOf(id) === -1) $grid.append(self._template_widget(template));
		});
		(this.state.custom || []).forEach(function (widget) {
			if (hidden.indexOf(widget.id) === -1) $grid.append(self._custom_widget(widget));
		});

		this._render_quick_create();
		this._render_reports_charts();
		this._render_apps_grid();
		this._start_live_widgets();
	}

	/* Shared wrapper: ID is persisted; size maps to a responsive CSS grid span. */
	_widget_shell(id, size, inner, extra_class) {
		return (
			'<section class="st-sh-widget ' + (extra_class || "") + '" ' +
				'data-widget-id="' + this._esc(id) + '" data-widget-size="' + size + '" draggable="false">' +
				'<div class="st-sh-drag-tools">' +
					'<button class="st-sh-remove-widget" type="button" title="' + __("Remove widget") + '" aria-label="' + __("Remove widget") + '">&times;</button>' +
					'<button class="st-sh-resize st-sh-resize-smaller" type="button" title="' + __("Make narrower") + '" aria-label="' + __("Make widget narrower") + '">&minus;</button>' +
					'<span class="st-sh-size-label" aria-hidden="true">' + this._size_label(size) + '</span>' +
					'<button class="st-sh-resize st-sh-resize-larger" type="button" title="' + __("Make wider") + '" aria-label="' + __("Make widget wider") + '">+</button>' +
					'<button class="st-sh-move st-sh-move-back" type="button" title="' + __("Move backward") + '" aria-label="' + __("Move backward") + '">' +
						'&larr;' +
					'</button>' +
					'<button class="st-sh-drag-handle" type="button" title="' + __("Drag to rearrange") + '" aria-label="' + __("Drag to rearrange") + '">' +
						'<span></span><span></span><span></span><span></span><span></span><span></span>' +
					'</button>' +
					'<button class="st-sh-move st-sh-move-forward" type="button" title="' + __("Move forward") + '" aria-label="' + __("Move forward") + '">' +
						'&rarr;' +
					'</button>' +
				'</div>' +
				inner +
			'</section>'
		);
	}

	_size_label(size) {
		return {
			quarter: "3/12",
			half: "4/12",
			medium: "6/12",
			wide: "8/12",
			full: "12/12",
		}[size] || "4/12";
	}

	_widget_templates() {
		return [
			{ id: "focus-clock", title: __("Focus Clock"), description: __("Current time and a calm focus cue"), icon: "clock", accent: "blue", size: "quarter" },
			{ id: "today-date", title: __("Today"), description: __("A clean daily date card"), icon: "calendar", accent: "coral", size: "quarter" },
			{ id: "scratch-pad", title: __("Scratch Pad"), description: __("Keep a quick note on your dashboard"), icon: "edit", accent: "amber", size: "half" },
			{ id: "useful-links", title: __("Useful Links"), description: __("Jump to Tasks, ToDos and reports"), icon: "link", accent: "green", size: "half" },
		];
	}

	_find_template(id) {
		return this._widget_templates().find(function (item) { return item.id === id; });
	}

	_template_widget(template) {
		var body = "";
		if (template.id === "focus-clock") {
			body = '<div class="st-sh-live-clock" data-live-clock>--:--</div><div class="st-sh-live-caption">' + __("One thing at a time.") + '</div>';
		} else if (template.id === "today-date") {
			body = '<div class="st-sh-date-widget"><strong data-date-day></strong><span data-date-month></span></div>';
		} else if (template.id === "scratch-pad") {
			body = '<textarea class="st-sh-scratch-input" maxlength="500" placeholder="' + __("Type a quick note...") + '">' + this._esc(this.state.scratch || "") + '</textarea>';
		} else {
			body = '<div class="st-sh-useful-links"><a href="/desk/task">' + __("Tasks") + ' <span>&rarr;</span></a>' +
				'<a href="/desk/todo">' + __("ToDos") + ' <span>&rarr;</span></a><a href="/desk/query-report">' + __("Reports") + ' <span>&rarr;</span></a></div>';
		}
		return this._panel_widget(template.id, template.title, template.description, template.icon, template.size, '<div class="st-sh-card-body">' + body + '</div>');
	}

	_custom_widget(widget) {
		var value = this._esc(widget.value || "");
		var body;
		if (widget.type === "link") {
			var href = this._safe_url(widget.url);
			body = '<a class="st-sh-custom-link" href="' + href + '"><span>' + (value || __("Open")) + '</span><b>&rarr;</b></a>';
		} else if (widget.type === "number") {
			body = '<div class="st-sh-custom-number">' + (value || "0") + '</div>';
		} else {
			body = '<div class="st-sh-custom-note">' + (value || __("Empty note")) + '</div>';
		}
		return this._widget_shell(
			widget.id,
			widget.size || "half",
			'<div class="st-sh-card st-sh-custom-card st-sh-tone-' + (widget.accent || "blue") + '">' +
				'<div class="st-sh-card-head"><div class="st-sh-card-heading"><span class="st-sh-card-icon">' +
				this._icon(widget.type === "link" ? "link" : (widget.type === "number" ? "chart" : "edit"), "sm") +
				'</span><div><h3>' + this._esc(widget.title || __("My widget")) + '</h3><p>' + __("Custom widget") + '</p></div></div></div>' +
				'<div class="st-sh-card-body">' + body + '</div></div>',
			"st-sh-panel-widget st-sh-user-widget"
		);
	}

	/* KPI content remains a normal Desk link outside customization mode. */
	_kpi_widget(kpi) {
		var inner =
			'<a href="' + kpi.route + '" class="st-sh-kpi-link" tabindex="0">' +
				'<div class="st-sh-kpi-top">' +
					'<span class="st-sh-kpi-icon">' + this._icon(kpi.icon, "md") + '</span>' +
					'<span class="st-sh-kpi-trend" aria-hidden="true">&nearr;</span>' +
				'</div>' +
				'<div class="st-sh-kpi-num" data-kpi-value>—</div>' +
				'<div class="st-sh-kpi-label">' + kpi.label + '</div>' +
			'</a>';

		return this._widget_shell(
			kpi.id,
			"quarter",
			inner,
			"st-sh-kpi st-sh-tone-" + kpi.accent
		);
	}

	/* Common frame keeps operational panel markup and drag controls consistent. */
	_panel_widget(id, title, subtitle, icon, size, body) {
		var inner =
			'<div class="st-sh-card">' +
				'<div class="st-sh-card-head">' +
					'<div class="st-sh-card-heading">' +
						'<span class="st-sh-card-icon">' + this._icon(icon, "sm") + '</span>' +
						'<div><h3>' + title + '</h3><p>' + subtitle + '</p></div>' +
					'</div>' +
				'</div>' +
				body +
			'</div>';
		return this._widget_shell(id, size, inner, "st-sh-panel-widget");
	}

	/* Keep the upstream workspace launcher as a first-class dashboard widget. */
	_apps_widget() {
		var inner =
			'<div class="st-sh-card st-sh-apps-card">' +
				'<div class="st-sh-card-head st-sh-apps-head">' +
					'<div class="st-sh-card-heading">' +
						'<span class="st-sh-card-icon">' + this._icon("grid", "sm") + '</span>' +
						'<div><h3>' + __("Your Apps") + '</h3><p>' + __("Jump to any workspace") + '</p></div>' +
					'</div>' +
					'<a href="/desk/all-apps" class="st-sh-all-ws">' +
						__("View All Workspaces") + ' <span aria-hidden="true">&rarr;</span>' +
					'</a>' +
				'</div>' +
				'<div id="st-sh-apps" class="st-sh-apps-body"></div>' +
			'</div>';
		return this._widget_shell("your-apps", "full", inner, "st-sh-panel-widget");
	}

 	/* ★ Giám sát hệ thống (viewer-only entry to Trung tâm điều hành). Body lay
 	   `smart_edu_core.api.ops.get_ops_summary` (scope me truoc, scope site chi
 	   khi server tra co `site_allowed`): mini stat + thanh suc khoe job + top loi
 	   — chi so dem, khong PII (S7). */
 	_ops_widget() {
 		var ws_name = "Gi\u00e1m s\u00e1t v\u1eadn h\u00e0nh";
 		this._ops_workspace_name = ws_name;
 		var slug = (frappe.router && frappe.router.slug)
 			? frappe.router.slug(ws_name)
 			: ws_name;
 		var inner =
 			'<div class="st-sh-card st-sh-ops-card">' +
 				'<div class="st-sh-card-head st-sh-ops-head">' +
 					'<div class="st-sh-card-heading">' +
 						'<span class="st-sh-card-icon">' + this._icon("warning", "sm") + '</span>' +
 						'<div><h3>' + __("Giám sát hệ thống") + '</h3><p>' + __("Trung tâm công việc hàng ngày — theo dõi toàn hệ thống") + '</p></div>' +
 					'</div>' +
 					'<a href="/desk/' + encodeURIComponent(slug) + '" class="st-sh-all-ws" data-ops-link="' + slug + '">' +
 						__("Mở trung tâm điều hành") + ' <span aria-hidden="true">&rarr;</span>' +
 					'</a>' +
 				'</div>' +
 				'<div class="st-sh-card-body st-sh-ops-body">' +
 					'<div class="st-sh-ops-stats" data-ops-stats><div class="st-sh-spin"></div></div>' +
 					'<div class="st-sh-ops-health" data-ops-health hidden></div>' +
 					'<div class="st-sh-ops-errors" data-ops-errors hidden></div>' +
 					'<div class="st-sh-ops-foot"><span data-ops-updated></span></div>' +
 				'</div>' +
 			'</div>';
 		return this._widget_shell("giam-sat-van-hanh", "full", inner, "st-sh-panel-widget");
 	}

	/* Filter before rendering so inaccessible DocTypes never enter the DOM. */
	_get_kpi_definitions() {
		var can_read = ((frappe.boot && frappe.boot.user && frappe.boot.user.can_read) || []);
		return [
			{
				id: "unpaid-invoices",
				label: __("Unpaid Invoices"),
				dt: "Sales Invoice",
				filters: { status: ["in", ["Unpaid", "Overdue"]], docstatus: 1 },
				route: "/desk/sales-invoice?status=Unpaid",
				icon: "file-text",
				accent: "amber",
			},
			{
				id: "open-orders",
				label: __("Open Orders"),
				dt: "Sales Order",
				filters: { status: ["in", ["To Deliver and Bill", "To Bill", "To Deliver"]], docstatus: 1 },
				route: "/desk/sales-order",
				icon: "shopping-cart",
				accent: "blue",
			},
			{
				id: "open-tasks",
				label: __("Open Tasks"),
				dt: "Task",
				/* Task KHONG co field allocated_to (do container 10/11/2026) —
				   filter allocated_to o day nem popup "Field not permitted"
				   cho MOI user (UAT 10/11). Giu dem site-wide nhu cu; dem dung
				   theo user can backend join (deferred, can PM duyet API moi). */
				filters: { status: "Open" },
				route: "/desk/task?status=Open",
				icon: "list-todo",
				accent: "green",
			},
			{
				id: "my-todos",
				label: __("My ToDos"),
				dt: "ToDo",
				/* Scope theo cá nhân — KHÔNG phát “My ToDos” đếm toàn site (Frappe
				   `can_read` cho role “All” đọc mọi ToDo ⇒ sai nghiệp vụ + rủi ro
				   riêng tư). Phải có `allocated_to` bằng user hiện tại. */
				filters: { status: "Open", allocated_to: frappe.session.user },
				route: "/desk/todo?status=Open",
				icon: "circle-check",
				accent: "coral",
			},
		].filter(function (kpi) {
			return can_read.indexOf(kpi.dt) !== -1;
		});
	}

	/* ── 5. LAYOUT EDITING / DRAG AND DROP ───────────────────────────────────
	   HTML5 drag handles pointer reordering; arrows provide a keyboard fallback. */
	_bind_layout_events() {
		var self = this;
		var $grid = this.$body.find("#st-sh-widget-grid");

		this.$body.on("click.st_sh_layout", ".st-sh-add-widgets", function () {
			self._set_library(true);
		});
		this.$body.on("click.st_sh_layout", ".st-sh-library-close, .st-sh-library-backdrop", function () {
			self._set_library(false);
		});
		this.$body.on("click.st_sh_layout", ".st-sh-library-item", function () {
			self._add_template(this.dataset.templateId);
		});
		this.$body.on("dragstart.st_sh_library", ".st-sh-library-item", function (event) {
			self.library_drag_id = this.dataset.templateId;
			var original = event.originalEvent;
			if (original && original.dataTransfer) {
				original.dataTransfer.effectAllowed = "copy";
				original.dataTransfer.setData("text/plain", self.library_drag_id);
			}
			self.$body.find(".st-smart-home").addClass("st-sh-library-dragging");
		});
		this.$body.on("dragend.st_sh_library", ".st-sh-library-item", function () {
			self.library_drag_id = null;
			self.$body.find(".st-smart-home").removeClass("st-sh-library-dragging");
		});
		$grid.on("dragover.st_sh_library", function (event) {
			if (!self.library_drag_id) return;
			event.preventDefault();
		});
		$grid.on("drop.st_sh_library", function (event) {
			if (!self.library_drag_id || $(event.target).closest(".st-sh-widget").length) return;
			event.preventDefault();
			self._add_template(self.library_drag_id);
			self.library_drag_id = null;
		});

		this.$body.on("click.st_sh_layout", ".st-sh-build-widget", function () {
			self._set_library(false);
			self._set_builder(true);
		});
		this.$body.on("click.st_sh_layout", ".st-sh-builder-close, .st-sh-builder-backdrop", function (event) {
			if (event.target === this) self._set_builder(false);
		});
		this.$body.on("click.st_sh_layout", ".st-sh-builder", function (event) {
			event.stopPropagation();
		});
		this.$body.on("change.st_sh_layout input.st_sh_layout", ".st-sh-builder-form input, .st-sh-builder-form textarea, .st-sh-builder-form select", function () {
			self._update_builder_preview();
		});
		this.$body.on("change.st_sh_layout", '.st-sh-builder-form [name="type"]', function () {
			var is_link = this.value === "link";
			self.$body.find(".st-sh-builder-url").prop("hidden", !is_link);
			self._update_builder_preview();
		});
		this.$body.on("submit.st_sh_layout", ".st-sh-builder-form", function (event) {
			event.preventDefault();
			self._create_custom_widget(this);
		});

		/* Links are disabled while editing to prevent accidental navigation. */
		this.$body.on("click.st_sh_layout", ".st-sh-customize", function () {
			self._set_editing(!self.editing);
		});

		this.$body.on("click.st_sh_layout", ".st-sh-reset", function () {
			frappe.confirm(__("Reset your Smart Home widget order?"), function () {
				try {
					localStorage.removeItem(self.storage_key);
				} catch (e) {}
				self.state = { order: [], added: [], custom: [], hidden: [], scratch: "", sizes: {} };
				self.$body.find("#st-sh-widget-grid").empty();
				self._render_widgets();
				self._restore_layout();
				self._set_editing(self.editing);
				self._announce_saved(__("Default layout restored"));
			});
		});

		this.$body.on("click.st_sh_layout", ".st-sh-remove-widget", function (event) {
			event.preventDefault();
			event.stopPropagation();
			var widget = this.closest(".st-sh-widget");
			if (!widget) return;
			self._remove_widget(widget.dataset.widgetId);
		});

		this.$body.on("click.st_sh_layout", ".st-sh-resize", function (event) {
			event.preventDefault();
			event.stopPropagation();
			var widget = this.closest(".st-sh-widget");
			if (!widget || !self.editing) return;
			self._resize_widget(widget, this.classList.contains("st-sh-resize-larger") ? 1 : -1);
		});

		this.$body.on("input.st_sh_layout", ".st-sh-scratch-input", function () {
			self.state.scratch = this.value;
			self._save_layout(false);
		});

		/* Move the existing node so loaded values and event bindings survive. */
		this.$body.on("click.st_sh_layout", ".st-sh-move", function (event) {
			event.preventDefault();
			event.stopPropagation();
			var widget = this.closest(".st-sh-widget");
			if (!widget || !self.editing) return;
			if (this.classList.contains("st-sh-move-back") && widget.previousElementSibling) {
				widget.parentNode.insertBefore(widget, widget.previousElementSibling);
			} else if (
				this.classList.contains("st-sh-move-forward") &&
				widget.nextElementSibling
			) {
				widget.parentNode.insertBefore(widget.nextElementSibling, widget);
			}
			self._save_layout();
			widget.focus({ preventScroll: true });
		});

		this.$body.on("click.st_sh_layout", ".st-sh-widget a", function (event) {
			if (self.editing) {
				event.preventDefault();
				event.stopPropagation();
			}
		});

		/* Keep one active source and expose a stable ID to browser drag tooling. */
		$grid.on("dragstart.st_sh_layout", ".st-sh-widget", function (event) {
			if (!self.editing) {
				event.preventDefault();
				return;
			}
			self.dragged = this;
			this.classList.add("st-sh-dragging");
			var original = event.originalEvent;
			if (original && original.dataTransfer) {
				original.dataTransfer.effectAllowed = "move";
				original.dataTransfer.setData("text/plain", this.dataset.widgetId);
			}
		});

		/* Pointer midpoint decides whether insertion occurs before or after. */
		$grid.on("dragover.st_sh_layout", ".st-sh-widget", function (event) {
			if (!self.dragged || this === self.dragged) return;
			event.preventDefault();
			$grid.find(".st-sh-drop-before, .st-sh-drop-after")
				.removeClass("st-sh-drop-before st-sh-drop-after");
			var original = event.originalEvent;
			var rect = this.getBoundingClientRect();
			var after = original.clientY > rect.top + rect.height / 2;
			this.classList.add(after ? "st-sh-drop-after" : "st-sh-drop-before");
		});

		$grid.on("drop.st_sh_layout", ".st-sh-widget", function (event) {
			if (self.library_drag_id) {
				event.preventDefault();
				event.stopPropagation();
				self._add_template(self.library_drag_id);
				self.library_drag_id = null;
				return;
			}
			if (!self.dragged || this === self.dragged) return;
			event.preventDefault();
			var target = this;
			var put_after = target.classList.contains("st-sh-drop-after");
			target.parentNode.insertBefore(
				self.dragged,
				put_after ? target.nextElementSibling : target
			);
			self._finish_drag(true);
		});

		$grid.on("dragend.st_sh_layout", ".st-sh-widget", function () {
			self._finish_drag(false);
		});
	}

	/* Toggle every edit-only affordance from one authoritative state. */
	_set_editing(enabled) {
		this.editing = enabled === true;
		var $home = this.$body.find(".st-smart-home");
		var $button = this.$body.find(".st-sh-customize");
		$home.toggleClass("st-sh-is-editing", this.editing);
		$button.attr("aria-pressed", this.editing ? "true" : "false");
		$button.find(".st-sh-customize-label").text(
			this.editing ? __("Done") : __("Customize layout")
		);
		this.$body.find("#st-sh-widget-grid > .st-sh-widget").attr("draggable", this.editing ? "true" : "false");
		if (this.editing) {
			this.$body.find("#st-sh-widget-grid > .st-sh-widget").attr("tabindex", "0").first().focus();
		} else {
			this.$body.find("#st-sh-widget-grid > .st-sh-widget").removeAttr("tabindex");
		}
	}

	_set_library(open) {
		var $library = this.$body.find(".st-sh-library");
		this.$body.find(".st-sh-library-backdrop").prop("hidden", !open);
		$library.toggleClass("is-open", open).attr("aria-hidden", open ? "false" : "true");
		if (open) $library.find(".st-sh-library-close").focus();
	}

	_set_builder(open) {
		var $backdrop = this.$body.find(".st-sh-builder-backdrop");
		$backdrop.prop("hidden", !open).toggleClass("is-open", open);
		if (open) {
			this._update_builder_preview();
			$backdrop.find('[name="title"]').focus();
		}
	}

	_add_template(id) {
		var template = this._find_template(id);
		if (!template) return;
		var exists = this.$body.find('[data-widget-id="' + id + '"]').length > 0;
		if (exists) {
			this._set_library(false);
			this._announce_saved(__("Widget is already on your dashboard"));
			return;
		}
		this.state.added = this.state.added || [];
		if (this.state.added.indexOf(id) === -1) this.state.added.push(id);
		this.state.hidden = (this.state.hidden || []).filter(function (hidden_id) { return hidden_id !== id; });
		var $widget = $(this._template_widget(template));
		var remembered_size = (this.state.sizes || {})[id];
		if (["quarter", "half", "medium", "wide", "full"].indexOf(remembered_size) > -1) {
			$widget.attr("data-widget-size", remembered_size);
			$widget.find(".st-sh-size-label").text(this._size_label(remembered_size));
		}
		if (this.editing) $widget.attr({ draggable: "true", tabindex: "0" });
		this.$body.find("#st-sh-widget-grid").append($widget);
		this._start_live_widgets();
		this._save_layout();
		this._set_library(false);
	}

	_create_custom_widget(form) {
		var data = new FormData(form);
		var widget = {
			id: "custom-" + Date.now().toString(36),
			type: String(data.get("type") || "note"),
			title: String(data.get("title") || __("My widget")).trim().slice(0, 48),
			value: String(data.get("value") || "").trim().slice(0, 240),
			url: String(data.get("url") || "").trim().slice(0, 300),
			size: ["quarter", "half", "wide"].indexOf(data.get("size")) > -1 ? data.get("size") : "half",
			accent: ["blue", "green", "amber", "coral"].indexOf(data.get("accent")) > -1 ? data.get("accent") : "blue",
		};
		this.state.custom = this.state.custom || [];
		this.state.custom.push(widget);
		var $widget = $(this._custom_widget(widget));
		if (this.editing) $widget.attr({ draggable: "true", tabindex: "0" });
		this.$body.find("#st-sh-widget-grid").append($widget);
		this._save_layout();
		this._set_builder(false);
		form.reset();
		this._announce_saved(__("Widget created"));
	}

	_update_builder_preview() {
		var form = this.$body.find(".st-sh-builder-form")[0];
		if (!form) return;
		var data = new FormData(form);
		var preview = {
			id: "preview",
			type: String(data.get("type") || "note"),
			title: String(data.get("title") || __("My widget")),
			value: String(data.get("value") || ""),
			url: String(data.get("url") || ""),
			size: "half",
			accent: String(data.get("accent") || "blue"),
		};
		this.$body.find("[data-builder-preview]").html(this._custom_widget(preview));
	}

	_remove_widget(id) {
		var custom_index = (this.state.custom || []).findIndex(function (item) { return item.id === id; });
		if (custom_index > -1) {
			this.state.custom.splice(custom_index, 1);
		} else {
			this.state.added = (this.state.added || []).filter(function (item) { return item !== id; });
			this.state.hidden = this.state.hidden || [];
			if (this.state.hidden.indexOf(id) === -1) this.state.hidden.push(id);
		}
		this.$body.find('[data-widget-id="' + id + '"]').remove();
		this._save_layout();
	}

	_resize_widget(widget, direction) {
		var sizes = ["quarter", "half", "medium", "wide", "full"];
		var current = sizes.indexOf(widget.dataset.widgetSize);
		if (current < 0) current = 1;
		var next = Math.max(0, Math.min(sizes.length - 1, current + direction));
		var size = sizes[next];
		widget.dataset.widgetSize = size;
		var label = widget.querySelector(".st-sh-size-label");
		if (label) label.textContent = this._size_label(size);
		this.state.sizes = this.state.sizes || {};
		this.state.sizes[widget.dataset.widgetId] = size;
		this._save_layout();
	}

	/* Clear transient markers after cancel; persist only a successful drop. */
	_finish_drag(save) {
		this.$body.find("#st-sh-widget-grid > .st-sh-widget")
			.removeClass("st-sh-dragging st-sh-drop-before st-sh-drop-after");
		this.dragged = null;
		if (save) this._save_layout();
	}

	/* ── 6. PER-USER LAYOUT PERSISTENCE ──────────────────────────────────────
	   Only stable IDs are stored; content and permissions remain authoritative. */
	_save_layout(announce) {
		var order = this.$body.find("#st-sh-widget-grid > .st-sh-widget").map(function () {
			return this.dataset.widgetId;
		}).get();
		this.state.order = order;
		try {
			localStorage.setItem(this.storage_key, JSON.stringify(this.state));
		} catch (e) {}
		if (announce !== false) this._announce_saved(__("Layout saved"));
	}

	_restore_layout() {
		var $grid = this.$body.find("#st-sh-widget-grid");
		var order = Array.isArray(this.state.order) ? this.state.order : [];
		var known = {};
		$grid.children(".st-sh-widget").each(function () {
			known[this.dataset.widgetId] = this;
		});
		order.forEach(function (id) {
			if (known[id]) $grid.append(known[id]);
		});

		/* v3 key = layout moi hoan toan, khong con saved order cu de migrate:
		   DOM order o _render_widgets da la thu tu uu tien. */

		/* Other newly-added or newly-permitted widgets append instead of
		   disappearing from an older saved layout that does not know their IDs. */
		Object.keys(known).forEach(function (id) {
			if (order.indexOf(id) === -1) $grid.append(known[id]);
		});

		var sizes = this.state.sizes || {};
		var self = this;
		$grid.children(".st-sh-widget").each(function () {
			var size = sizes[this.dataset.widgetId];
			if (["quarter", "half", "medium", "wide", "full"].indexOf(size) === -1) return;
			this.dataset.widgetSize = size;
			var label = this.querySelector(".st-sh-size-label");
			if (label) label.textContent = self._size_label(size);
		});
	}

	_load_layout() {
		var saved = null;
		try {
			saved = JSON.parse(localStorage.getItem(this.storage_key) || "null");
		} catch (e) {}
		return saved && typeof saved === "object" ? {
			order: Array.isArray(saved.order) ? saved.order : [],
			added: Array.isArray(saved.added) ? saved.added : [],
			custom: Array.isArray(saved.custom) ? saved.custom : [],
			hidden: Array.isArray(saved.hidden) ? saved.hidden : [],
			scratch: typeof saved.scratch === "string" ? saved.scratch : "",
			sizes: saved.sizes && typeof saved.sizes === "object" ? saved.sizes : {},
		} : { order: [], added: [], custom: [], hidden: [], scratch: "", sizes: {} };
	}

	_start_live_widgets() {
		var self = this;
		function update() {
			var now = new Date();
			self.$body.find("[data-live-clock]").text(now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
			self.$body.find("[data-date-day]").text(now.getDate());
			self.$body.find("[data-date-month]").text(now.toLocaleDateString(self._site_locale(), { weekday: "long", month: "long" }));
		}
		update();
		if (!this._clock_timer) this._clock_timer = setInterval(update, 30000);
		/* Realtime nhe: ops + my-day poll lai 2 phut (API chi dem, re). */
		if (!this._ops_timer) {
			this._ops_timer = setInterval(function () {
				self._refresh_ops();
				self._refresh_today();
			}, 120000);
		}
	}

	/* Inline feedback avoids showing a global toast after every small movement. */
	_announce_saved(message) {
		var $state = this.$body.find(".st-sh-save-state");
		$state.text(message).addClass("is-visible");
		clearTimeout(this._save_timer);
		this._save_timer = setTimeout(function () {
			$state.removeClass("is-visible");
		}, 1800);
	}

	/* ── 7. LIVE KPI COUNTS ──────────────────────────────────────────────────
	   Requests are independent so one failed DocType cannot block other KPIs. */
	_refresh_kpis() {
		var self = this;
		this.kpis.forEach(function (kpi) {
			var $num = self.$body
				.find('[data-widget-id="' + kpi.id + '"] [data-kpi-value]');
			if (kpi.id === "open-tasks") {
				if (typeof frappe.xcall !== "function") {
					$num.text("—");
					return;
				}
				frappe.xcall("smart_edu_core.api.ops.get_my_open_tasks").then(
					function (result) {
						var count = result && result.count;
						$num.text(count !== undefined && count !== null ? count : "—");
					},
					function () {
						$num.text("—");
					}
				);
				return;
			}
			frappe.call({
				method: "frappe.client.get_count",
				args: { doctype: kpi.dt, filters: kpi.filters },
				callback: function (response) {
					$num.text(response.message !== undefined ? response.message : "—");
				},
				error: function () {
					$num.text("—");
				},
			});
		});
	}

	/* ── 8. RECENT DOCUMENTS ─────────────────────────────────────────────────
	   Route history is instant and avoids an unnecessary server-side query. */
	_refresh_recent() {
		var $container = this.$body.find("#st-sh-recent");
		var history = (frappe.route_history || []).slice().reverse();
		var seen = {};
		var items = [];

		/* De-duplicate repeated visits while retaining most-recent-first order. */
		for (var index = 0; index < history.length && items.length < 8; index++) {
			var route = history[index];
			if (
				route[0] === "Form" &&
				route[1] &&
				route[2] &&
				/* Bo qua DocType User: docname la email, hien len vo nghia. */
				route[1] !== "User" &&
				!String(route[2]).startsWith("new-")
			) {
				var key = route[1] + "::" + route[2];
				if (!seen[key]) {
					seen[key] = true;
					items.push({ doctype: route[1], name: route[2] });
				}
			}
		}

		if (!items.length) {
			$container.html(
				'<div class="st-sh-empty">' +
					this._icon("clock", "md") +
					'<span>' + __("No recent documents yet. Open a record and it will appear here.") + '</span>' +
				'</div>'
			);
			return;
		}

		var self = this;
		$container.html(items.map(function (item) {
			var slug = frappe.router.slug(item.doctype);
			var url = "/desk/" + slug + "/" + encodeURIComponent(item.name);
			return (
				'<a href="' + url + '" class="st-sh-doc-row">' +
					'<span class="st-sh-doc-mark"></span>' +
					'<span class="st-sh-doc-copy">' +
						'<span class="st-sh-doc-name">' + self._esc(item.name) + '</span>' +
						'<span class="st-sh-doc-dt">' + self._esc(__(item.doctype)) + '</span>' +
					'</span>' +
					'<span class="st-sh-row-arrow" aria-hidden="true">&rarr;</span>' +
				'</a>'
			);
		}).join(""));
	}

	/* ── 9. QUICK CREATE ─────────────────────────────────────────────────────
	   Static session permissions determine a compact, predictable action list. */
	_render_quick_create() {
		var $container = this.$body.find("#st-sh-qc");
		var can_create = ((frappe.boot && frappe.boot.user && frappe.boot.user.can_create) || []);
		var order = [
			"Sales Invoice", "Quotation", "Sales Order", "Purchase Order",
			"Purchase Invoice", "Expense Claim", "Leave Application",
			"Customer", "Supplier", "Task", "ToDo",
		];
		var items = order.filter(function (doctype) {
			return can_create.indexOf(doctype) !== -1;
		}).slice(0, 6);

		if (!items.length) {
			$container.html('<div class="st-sh-empty"><span>' + __("No create permissions found.") + '</span></div>');
			return;
		}

		$container.html('<div class="st-sh-qc-grid">' + items.map(function (doctype) {
			var slug = frappe.router.slug(doctype);
			return (
				'<a href="/desk/' + slug + '/new" class="st-sh-qc-item">' +
					'<span class="st-sh-qc-plus">+</span>' +
					'<span>' + __(doctype) + '</span>' +
				'</a>'
			);
		}).join("") + '</div>');
	}

	/* Reuse module_cards.js so Today's View and All Apps stay identical. */
	_render_apps_grid() {
		var $row = this.$body.find("#st-sh-apps");
		var wc = sanpra_uiv16.workspaceCards;
		if (!$row.length || !wc) return;

		$row.html(wc.buildSkeletons(8));
		var self = this;

		wc.fetchWorkspaces(function (pages) {
			/* Loc tile ky thuat tieng Anh (PM quyet 10/11/2026): Build, HR Setup,
			   Tenure, Invoicing, Payments, Recruitment, Accounting — van vao duoc
			   qua sidebar, chi an tren luoi Smart Home. So khop tren title chuan
			   hoa (khong dau, lower) de chiu duoc dich label. */
			var HIDDEN_APPS = ["build", "hr setup", "tenure", "invoicing", "payments", "recruitment", "accounting"];
			function normTitle(value) {
				/* Chuan hoa de so khop: lower + bo dau (title co the da Viet hoa). */
				var s = String(value || "").toLowerCase();
				try {
					s = s.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
				} catch (e) {}
				return s.replace(/đ/g, "d");
			}
			function isHidden(page) {
				return (
					HIDDEN_APPS.indexOf(normTitle(page && page.name)) !== -1 ||
					HIDDEN_APPS.indexOf(normTitle(page && page.title)) !== -1
				);
			}
			var visible = (pages || []).filter(function (p) {
				return !isHidden(p);
			});
			/* Hiển thị 12 mục đầu (tăng từ 8) — tổng workspace của hệ thống
			   (~10) phải lọt hết vào lưới mà cần cuộn — `slice(0, 8)` cũ khiến
			   "Giám sát vận hành" (sequence 21) rớt khỏi 8 ô đầu. */
			var items = visible.slice(0, 12);

			/* Ops entry (Giám sát vận hành): chỉ hiện khi user có quyền xem (pool
			   đã lọc theo role ở server) — cùng gate với icon header ops. */
			self.$body.find('[data-widget-id="giam-sat-van-hanh"]').each(function () {
				var ws = self._ops_workspace_name;
				var has = (pages || []).some(function (p) { return p.name === ws; });
				if (has) $(this).css("display", "");
				else $(this).remove();
			});
			if (!items.length) {
				$row.html('<div class="st-ws-cards"><div class="st-sh-empty">' + __("No workspaces found.") + '</div></div>');
				return;
			}

			$row.html('<div class="st-ws-cards">' + items.map(function (p, idx) {
				return wc.buildCard(p, idx);
			}).join("") + '</div>');

			$row.find(".st-ws-card[data-ws]").each(function () {
				var slug = this.getAttribute("data-ws");
				this.addEventListener("click", function (e) {
					e.preventDefault();
					if (slug) frappe.set_route(slug);
				});
			});
		});
	}

	/* ── 10. NEEDS ATTENTION ─────────────────────────────────────────────────
	   Permission-safe counts run in parallel and render as one settled batch. */
	_refresh_pending() {
		var $container = this.$body.find("#st-sh-pending");
		var can_read = ((frappe.boot && frappe.boot.user && frappe.boot.user.can_read) || []);
		var checks = [
			{
				dt: "Sales Invoice",
				filters: { status: "Overdue", docstatus: 1 },
				label: __("{0} overdue sales invoices"),
				route: "/desk/sales-invoice?status=Overdue",
			},
			{
				/* Hoc phi qua han: Fees KHONG co field status (do that Education
				   container 10/11/2026) — loc theo due_date + outstanding_amount. */
				dt: "Fees",
				filters: { due_date: ["<", frappe.datetime.nowdate()], outstanding_amount: [">", 0], docstatus: 1 },
				label: __("{0} overdue tuition fees"),
				route: "/desk/fees",
			},
			{
				dt: "Purchase Order",
				filters: { status: "To Receive and Bill", docstatus: 1 },
				label: __("{0} pending purchase orders"),
				route: "/desk/purchase-order",
			},
			{
				dt: "Leave Application",
				filters: { status: "Open", docstatus: 0 },
				label: __("{0} leave applications awaiting approval"),
				route: "/desk/leave-application?status=Open",
			},
			{
				dt: "Expense Claim",
				filters: { status: "Draft", docstatus: 0 },
				label: __("{0} expense claims pending"),
				route: "/desk/expense-claim",
			},
		].filter(function (check) {
			return can_read.indexOf(check.dt) !== -1;
		});

		if (!checks.length) {
			this._render_all_clear($container);
			return;
		}

		var complete = 0;
		var found = [];
		var self = this;

		/* Shared completion count allows parallel requests and a single redraw. */
		checks.forEach(function (check) {
			frappe.call({
				method: "frappe.client.get_count",
				args: { doctype: check.dt, filters: check.filters },
				callback: function (response) {
					if (response.message > 0) {
						found.push({
							count: response.message,
							message: check.label.replace("{0}", response.message),
							route: check.route,
						});
					}
					if (++complete === checks.length) self._render_attention($container, found);
				},
				error: function () {
					if (++complete === checks.length) self._render_attention($container, found);
				},
			});
		});
	}

	/* ── 10b. OPS LIVE BODY ────────────────────────────────────────────────────
	   Mini stat + suc khoe job + top loi tu get_ops_summary (scope me truoc,
	   scope site chi khi server tra co `site_allowed`). Chi so dem, khong PII (S7).
	   Moi o deu la link nhu KPI Smart Home. */
	_refresh_ops() {
		var $stats = this.$body.find("[data-ops-stats]");
		if (!$stats.length) return;
		var $health = this.$body.find("[data-ops-health]");
		var $errors = this.$body.find("[data-ops-errors]");
		var $updated = this.$body.find("[data-ops-updated]");
		var self = this;

		function stat(label, route, value) {
			return '<a href="' + route + '" class="st-sh-ops-stat">' +
				'<span class="st-sh-ops-num">' + self._esc(value !== undefined && value !== null ? value : "—") + '</span>' +
				'<span class="st-sh-ops-cap">' + label + '</span></a>';
		}

		function render(summary, is_site) {
			var html =
				stat(__("Việc mở"), "/desk/todo?status=Open", summary.todos_open) +
				stat(__("Việc quá hạn"), "/desk/todo?status=Open", summary.todos_overdue) +
				stat(__("Sự kiện"), "/desk/event", summary.events_today) +
				stat(__("Chưa đọc"), "/desk/notification-log", summary.notifications_unread);
			if (is_site) {
				html +=
					stat(__("Lỗi 24 giờ"), "/desk/error-log", summary.errors_24h) +
					stat(__("Job lỗi 24 giờ"), "/desk/scheduled-job-log", summary.jobs_failed_24h);
			}
			$stats.html(html);
			var job_health = summary.job_status_summary;
			if (is_site && job_health) {
				var parts = [
					["ran", __("Chạy tốt")],
					["stale", __("Stale")],
					["never_ran", __("Chưa chạy")],
					["stopped", __("Đã dừng")],
				];
				var total = parts.reduce(function (n, p) {
					return n + (parseInt(job_health[p[0]], 10) || 0);
				}, 0) || 1;
				$health.html(
					'<div class="st-sh-ops-health-title">' + __("Sức khỏe job nền") + '</div>' +
					'<div class="st-sh-ops-bars">' + parts.map(function (p) {
						var v = parseInt(job_health[p[0]], 10) || 0;
						return '<div class="st-sh-ops-bar-row"><span>' + p[1] + ' ' + v + '</span>' +
							'<span class="st-sh-ops-bar"><i style="width:' + Math.round((v / total) * 100) + '%"></i></span></div>';
					}).join("") + '</div>'
				).prop("hidden", false);
			}
			var groups = summary.groups;
			if (is_site && groups && groups.length) {
				$errors.html(
					'<div class="st-sh-ops-health-title">' + __("Lỗi nhiều nhất 24 giờ") + '</div>' +
					groups.map(function (g) {
						return '<a href="/desk/error-log" class="st-sh-ops-err"><span>' +
							self._esc(g.method || "") + '</span><b>' + self._esc(g.count) + '</b></a>';
					}).join("")
				).prop("hidden", false);
			}
			if ($updated.length) $updated.text(__("Cập nhật") + " " + new Date().toLocaleTimeString());
		}

		function show_unavailable() {
			$stats.html('<div class="st-sh-empty"><span>' + __("Ops data unavailable.") + '</span></div>');
		}

		function render_me() {
			frappe.xcall("smart_edu_core.api.ops.get_ops_summary", { scope: "me" }).then(
				function (r) { render(r || {}, false); },
				show_unavailable
			);
		}
		if (typeof frappe.xcall !== "function") {
			render_me();
			return;
		}
		/* Gọi scope=me TRƯỚC: server trả `site_allowed` ⇒ biết ngay user có
		   được gọi scope=site không. Gọi site vô điều kiện ⇒ 403 ⇒ Frappe bắn
		   toast "Không được phép" cho mọi user không phải viewer (đo staging
		   12/11/2026 — PermissionError tại api/dashboard.py:195). */
		frappe.xcall("smart_edu_core.api.ops.get_ops_summary", { scope: "me" }).then(
			function (r) {
				r = r || {};
				if (!r.site_allowed) {
					render(r, false);
					return;
				}
				frappe.xcall("smart_edu_core.api.ops.get_ops_summary", { scope: "site" }).then(
					function (s) { render(s || {}, true); },
					function () { render(r, false); }
				);
			},
			show_unavailable
		);
	}

	/* ── 10c. MY DAY + REPORTS ────────────────────────────────────────────────
	   today-focus: so ca nhan tu scope me (sau fix O1 loc dung session user;
	   events_today la so chung cua site vi Event khong co truong ca nhan).
	   reports-charts: link tinh vao bao cao/bieu do dieu hanh, Frappe gate
	   quyen o trang dich. */
	_refresh_today() {
		/* Ngay cua toi = danh sach viec tiep theo (link thang ban ghi), KHONG
		   dem so — so dem da co tren KPI my-todos/open-tasks (tranh trung lap).
		   Trong het -> thu gon 1 dong all-clear thay vi 4 dong 0. */
		var $container = this.$body.find("#st-sh-today");
		if (!$container.length || typeof frappe.xcall !== "function") return;
		var self = this;
		function renderList(todos, summary) {
			summary = summary || {};
			var html = "";
			if (todos.length) {
				html += todos.map(function (td) {
					var title = td.description || td.name;
					return (
						'<a href="/desk/todo/' + encodeURIComponent(td.name) + '" class="st-sh-pending-row">' +
							'<span class="st-sh-todo-dot' + (td._overdue ? " st-sh-todo-late" : "") + '"></span>' +
							'<span class="st-sh-todo-name">' + self._esc(title) + '</span>' +
							'<span class="st-sh-todo-date">' + self._esc(td.date || "") + '</span>' +
							'<span class="st-sh-row-arrow" aria-hidden="true">&rarr;</span>' +
						'</a>'
					);
				}).join("");
			} else {
				html += '<div class="st-sh-all-clear"><span class="st-sh-clear-check">✓</span>' +
					'<div><strong>' + __("All clear") + '</strong></div></div>';
			}
			var foot = [];
			if (summary.events_today) foot.push('<a href="/desk/event">' + self._esc(summary.events_today) + " " + __("events today") + "</a>");
			if (summary.notifications_unread) foot.push('<a href="/desk/notification-log">' + self._esc(summary.notifications_unread) + " " + __("unread") + "</a>");
			if (foot.length) html += '<div class="st-sh-today-foot">' + foot.join(" · ") + "</div>";
			$container.html(html);
		}
		function loadTodos(summary) {
			frappe.call({
				method: "frappe.client.get_list",
				args: {
					doctype: "ToDo",
					fields: ["name", "description", "date"],
					filters: { status: "Open", allocated_to: frappe.session.user },
					limit_page_length: 5,
					order_by: "date asc",
				},
				callback: function (response) {
					var today = frappe.datetime.nowdate();
					var todos = (response.message || []).slice(0, 5).map(function (td) {
						td._overdue = td.date && td.date < today;
						return td;
					});
					todos.sort(function (a, b) { return (b._overdue ? 1 : 0) - (a._overdue ? 1 : 0); });
					renderList(todos, summary);
				},
				error: function () {
					renderList([], summary);
				},
			});
		}
		if (typeof frappe.call !== "function") {
			renderList([], {});
			return;
		}
		frappe.xcall("smart_edu_core.api.ops.get_ops_summary", { scope: "me" }).then(
			function (summary) {
				loadTodos(summary || {});
			},
			function () {
				loadTodos({});
			}
		);
	}

	_render_reports_charts() {
		var $container = this.$body.find("#st-sh-rc");
		if (!$container.length) return;
		/* 6 hang muc bao cao — khong ve bieu do (user: loai bo bieu do,
		   giu 6 link bao cao). */
		var items = [
			{ label: __("Hiệu quả giáo viên"), route: "/desk/query-report/hieu-qua-giao-vien" },
			{ label: __("Học phí đến hạn hôm nay"), route: "/desk/query-report/hoc-phi-den-han-hom-nay" },
			{ label: __("Doanh thu theo tháng"), route: "/desk/dashboard-chart/" + encodeURIComponent("Doanh thu theo tháng") },
			{ label: __("Công nợ theo tháng"), route: "/desk/dashboard-chart/" + encodeURIComponent("Công nợ theo tháng") },
			{ label: __("Hóa đơn học phí"), route: "/desk/sales-invoice" },
			{ label: __("Phiếu thu"), route: "/desk/payment-entry" },
		];
		$container.html('<div class="st-sh-qc-grid">' + items.map(function (item) {
			return (
				'<a href="' + item.route + '" class="st-sh-qc-item">' +
					'<span class="st-sh-qc-plus">&rarr;</span>' +
					'<span>' + item.label + '</span>' +
				'</a>'
			);
		}).join("") + '</div>');
	}

	/* Non-zero results become actionable rows after the request batch settles. */
	_render_attention($container, found) {
		if (!found.length) {
			this._render_all_clear($container);
			return;
		}
		var self = this;
		$container.html(found.map(function (item) {
			return (
				'<a href="' + item.route + '" class="st-sh-pending-row">' +
					'<span class="st-sh-pending-count">' + self._esc(item.count) + '</span>' +
					'<span>' + self._esc(item.message) + '</span>' +
					'<span class="st-sh-row-arrow" aria-hidden="true">&rarr;</span>' +
				'</a>'
			);
		}).join(""));
	}

	/* Positive empty state makes a zero-result attention widget intentional. */
	_render_all_clear($container) {
		$container.html(
			'<div class="st-sh-all-clear">' +
				'<span class="st-sh-clear-check">✓</span>' +
				'<div><strong>' + __("All clear") + '</strong><span>' +
					__("Nothing needs your attention right now.") +
				'</span></div>' +
			'</div>'
		);
	}

	/* ── 11. SAFE UI HELPERS ─────────────────────────────────────────────────
	   Icon lookup fails softly across Frappe versions; dynamic text is escaped. */
	_site_locale() {
		/* Ngay thang theo ngon ngu site (vi -> vi-VN), khong theo locale
		   trinh duyet — tranh "Tuesday, November 10, 2026" tren site tieng Viet. */
		var lang = (frappe.boot && frappe.boot.lang) || "en";
		return lang === "vi" ? "vi-VN" : lang;
	}
	_icon(name, size) {
		try {
			return frappe.utils.icon(name, size || "sm") || "";
		} catch (e) {
			return "";
		}
	}

	_esc(value) {
		return String(value === undefined || value === null ? "" : value)
			.replace(/&/g, "&amp;")
			.replace(/</g, "&lt;")
			.replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;")
			.replace(/'/g, "&#039;");
	}

	_safe_url(value) {
		var url = String(value || "").trim();
		if (/^(\/(?!\/)|https?:\/\/)/i.test(url)) return this._esc(url);
		return "#";
	}
};
