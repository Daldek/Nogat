// Hydrolog mockup interactions: theme, host mode (alone or in Nogat's shell), sections of the
// rail, panels and phone sheets, resizers, segmented controls and their panes, variants on the
// charts, explanations (i), menus, searchable command lists, validation of the catalog form,
// copying commands and toasts.
(function () {
  "use strict";

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var phone = window.matchMedia("(max-width: 860px)");
  var root = document.documentElement;

  function load(key) {
    try { return JSON.parse(localStorage.getItem(key)); } catch (e) { return null; }
  }
  function save(key, value) {
    try { localStorage.setItem(key, typeof value === "string" ? value : JSON.stringify(value)); } catch (e) {}
  }
  function stored(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }

  // ---------- Toast ----------
  var toast = $("#toast");
  var toastTimer = 0;
  function showToast(text) {
    toast.textContent = text;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.hidden = true; }, 3200);
  }

  // ---------- Theme (shared key with the other Nogat mockups) ----------
  var THEME_KEY = "nogat-theme";
  function setTheme(choice) {
    if (choice === "light" || choice === "dark") root.dataset.theme = choice;
    else delete root.dataset.theme;
    $$("[data-theme-set]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.dataset.themeSet === choice));
    });
  }
  $$("[data-theme-set]").forEach(function (b) {
    b.addEventListener("click", function () {
      save(THEME_KEY, b.dataset.themeSet);
      setTheme(b.dataset.themeSet);
    });
  });
  var storedTheme = stored(THEME_KEY);
  setTheme(storedTheme === "light" || storedTheme === "dark" ? storedTheme : "auto");

  // ---------- Host mode: Hydrolog alone or as a module in Nogat's shell ----------
  var HOST_KEY = "hydrolog-mockup-host";
  function setHost(host) {
    root.dataset.host = host;
    $$("[data-host-set]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.dataset.hostSet === host));
    });
  }
  $$("[data-host-set]").forEach(function (b) {
    b.addEventListener("click", function () {
      save(HOST_KEY, b.dataset.hostSet);
      setHost(b.dataset.hostSet);
      closeFloating();
    });
  });
  var hostParam = new URLSearchParams(window.location.search).get("host");
  var storedHost = stored(HOST_KEY);
  setHost(hostParam === "nogat" || hostParam === "standalone" ? hostParam : (storedHost === "nogat" ? "nogat" : "standalone"));

  // ---------- Sections of the rail ----------
  var SECTIONS = ["hydrogram", "siec", "statystyka", "kalkulatory", "polecenia"];
  var main = $("#main");
  function sectionFromHash() {
    var h = window.location.hash.replace("#", "");
    return SECTIONS.indexOf(h) >= 0 ? h : "hydrogram";
  }
  function activeView() {
    return $(".view-layout:not([hidden])", main);
  }

  // ---------- Panels: desktop columns and phone sheets ----------
  var reveals = [];                      // keep the selected command of a list in view
  var state = {
    open: { left: true, right: true },   // desktop columns, shared by every section
    sheet: null,                         // open phone sheet of the active section
    width: { left: null, right: null }   // null = CSS default
  };

  function panel(side, view) { return $(".view-panel." + side, view || activeView()); }
  function openPanel(side) {
    if (phone.matches) state.sheet = side;
    else state.open[side] = true;
    render();
  }
  function closePanel(side) {
    if (phone.matches) { if (state.sheet === side) state.sheet = null; }
    else state.open[side] = false;
    render();
  }
  function togglePanel(side) {
    var isOpen = phone.matches ? state.sheet === side : state.open[side];
    if (isOpen) closePanel(side); else openPanel(side);
  }

  function render() {
    var view = activeView();
    ["left", "right"].forEach(function (side) {
      var p = panel(side, view);
      p.classList.toggle("open", state.sheet === side);
      p.classList.toggle("collapsed", !state.open[side]);
      $(".resizer.r-" + side, view).hidden = !state.open[side];
    });
    $$("[data-open-panel]", view).forEach(function (b) {
      var side = b.dataset.openPanel;
      var wrap = b.closest(".phone-only") || b;
      wrap.classList.toggle("show", !state.open[side]);
      b.setAttribute("aria-expanded", String(phone.matches ? state.sheet === side : state.open[side]));
    });
    applyWidths();
  }

  $$("[data-open-panel]").forEach(function (b) {
    b.addEventListener("click", function () { togglePanel(b.dataset.openPanel); });
  });
  $$("[data-close-panel]").forEach(function (b) {
    b.addEventListener("click", function () { closePanel(b.dataset.closePanel); });
  });
  $$(".view-panel .grip").forEach(function (grip) {
    grip.addEventListener("click", function () {
      closePanel(grip.closest(".view-panel").classList.contains("left") ? "left" : "right");
    });
  });
  phone.addEventListener("change", function () { state.sheet = null; render(); });

  // ---------- Resizers (widths shared by every section) ----------
  var WIDTH_KEY = "hydrolog-mockup-widths";
  var LIMITS = { left: { min: 260, max: 560 }, right: { min: 340, max: 720 } };
  var CENTRE_MIN = 480;
  var other = { left: "right", right: "left" };

  function cssDefault(side) {
    var v = parseInt(getComputedStyle(root).getPropertyValue("--" + side + "-w"), 10);
    return isNaN(v) ? LIMITS[side].min : v;
  }
  function ownClamp(side, w) {
    return Math.min(LIMITS[side].max, Math.max(LIMITS[side].min, w));
  }
  function maxFor(side) {
    var o = other[side];
    var otherW = state.open[o] ? ownClamp(o, state.width[o] == null ? cssDefault(o) : state.width[o]) : 0;
    return Math.max(LIMITS[side].min, Math.min(LIMITS[side].max, main.clientWidth - otherW - CENTRE_MIN));
  }
  function clampWidth(side, w) {
    return Math.min(maxFor(side), Math.max(LIMITS[side].min, w));
  }
  function currentWidth(side) {
    return clampWidth(side, state.width[side] == null ? cssDefault(side) : state.width[side]);
  }
  function applyWidths() {
    ["left", "right"].forEach(function (side) {
      var prop = "--" + side + "-w";
      if (phone.matches) { main.style.removeProperty(prop); return; }
      if (!state.open[side]) { main.style.setProperty(prop, "0px"); return; }
      var w = currentWidth(side);
      main.style.setProperty(prop, w + "px");
      $$(".resizer.r-" + side).forEach(function (r) {
        r.setAttribute("aria-valuenow", String(w));
        r.setAttribute("aria-valuemax", String(maxFor(side)));
      });
    });
  }
  function setWidth(side, w) {
    state.width[side] = w == null ? null : clampWidth(side, w);
    applyWidths();
    save(WIDTH_KEY, state.width);
  }
  var storedWidths = load(WIDTH_KEY);
  if (storedWidths) {
    ["left", "right"].forEach(function (side) {
      if (typeof storedWidths[side] === "number") state.width[side] = ownClamp(side, storedWidths[side]);
    });
  }

  $$(".resizer").forEach(function (r) {
    var side = r.classList.contains("r-left") ? "left" : "right";
    var sign = side === "left" ? 1 : -1;   // the right panel grows when dragged left
    var drag = null;
    var lastDown = 0;

    // Double-click is detected here: preventDefault on pointerdown suppresses native dblclick.
    r.addEventListener("pointerdown", function (e) {
      if (phone.matches || e.button !== 0) return;
      e.preventDefault();
      r.focus();
      if (e.timeStamp - lastDown < 400) {
        lastDown = 0;
        setWidth(side, null);
        return;
      }
      lastDown = e.timeStamp;
      drag = { x: e.clientX, w: currentWidth(side) };
      r.setPointerCapture(e.pointerId);
      r.classList.add("dragging");
      document.body.classList.add("resizing");
    });
    r.addEventListener("pointermove", function (e) {
      if (!drag) return;
      if (Math.abs(e.clientX - drag.x) > 3) lastDown = 0;
      state.width[side] = clampWidth(side, drag.w + sign * (e.clientX - drag.x));
      applyWidths();
    });
    function endDrag() {
      if (!drag) return;
      drag = null;
      r.classList.remove("dragging");
      document.body.classList.remove("resizing");
      save(WIDTH_KEY, state.width);
    }
    r.addEventListener("pointerup", endDrag);
    r.addEventListener("pointercancel", endDrag);
    r.addEventListener("lostpointercapture", endDrag);

    r.addEventListener("keydown", function (e) {
      if (phone.matches) return;
      var step = e.shiftKey ? 64 : 16;
      var w = currentWidth(side);
      switch (e.key) {
        case "ArrowRight": setWidth(side, w + sign * step); break;
        case "ArrowLeft": setWidth(side, w - sign * step); break;
        case "Home": setWidth(side, LIMITS[side].min); break;
        case "End": setWidth(side, maxFor(side)); break;
        case "Enter": setWidth(side, null); break;
        default: return;
      }
      e.preventDefault();
    });
  });
  window.addEventListener("resize", applyWidths);

  function showSection(name) {
    $$(".view-layout", main).forEach(function (v) { v.hidden = v.dataset.section !== name; });
    $$(".rail-item[data-section]").forEach(function (a) {
      var on = a.dataset.section === name;
      a.classList.toggle("active", on);
      if (on) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    var view = activeView();
    $$(".crumb-section").forEach(function (el) { el.textContent = view.dataset.title; });
    $$(".crumb-context").forEach(function (el) { el.textContent = view.dataset.context; });
    document.title = "Hydrolog: " + view.dataset.title + " — " + view.dataset.context;
    closeFloating();
    state.sheet = null;
    render();
    reveals.forEach(function (fn) { fn(); });
    renderStatus();
  }
  window.addEventListener("hashchange", function () { showSection(sectionFromHash()); });
  $$('a[href="#"]').forEach(function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); });
  });

  // ---------- Segmented radio groups: panes, tabs, hints, command variants ----------
  function selectSeg(btn) {
    var group = btn.closest(".seg");
    $$("button", group).forEach(function (b) {
      var on = b === btn;
      b.classList.toggle("on", on);
      b.setAttribute("aria-checked", String(on));
      b.tabIndex = on ? 0 : -1;
    });
    if (group.dataset.panes) {
      $$('.pane[data-group="' + group.dataset.panes + '"]').forEach(function (p) {
        p.hidden = p.dataset.pane !== btn.dataset.pane;
      });
    }
    if (group.dataset.tabs) {
      var view = group.closest(".view-layout");
      $$("[data-tab-pane]", view).forEach(function (p) { p.hidden = p.dataset.tabPane !== btn.dataset.tab; });
    }
    if (group.dataset.hint) $("#" + group.dataset.hint).textContent = btn.dataset.hintText;
    if (group.dataset.cli) setCli(group.dataset.cli, btn.dataset.cliV);
    if (btn.dataset.infoTarget) $("#hg-uh-info").dataset.info = btn.dataset.infoTarget;
    if (group.dataset.panes === "pc-group") validateForm();
  }
  $$(".seg[role='radiogroup']").forEach(function (group) {
    var buttons = $$("button", group);
    buttons.forEach(function (b) {
      b.tabIndex = b.getAttribute("aria-checked") === "true" ? 0 : -1;
      b.addEventListener("click", function () { selectSeg(b); });
    });
    group.addEventListener("keydown", function (e) {
      var d = e.key === "ArrowRight" || e.key === "ArrowDown" ? 1 : e.key === "ArrowLeft" || e.key === "ArrowUp" ? -1 : 0;
      if (!d) return;
      e.preventDefault();
      var i = buttons.indexOf(document.activeElement);
      var next = buttons[(i + d + buttons.length) % buttons.length];
      next.focus();
      next.click();
    });
  });
  function selectTab(viewSection, tab) {
    var btn = $('.view-layout[data-section="' + viewSection + '"] [data-tab="' + tab + '"]');
    if (btn) selectSeg(btn);
  }

  // Command shown for a variant or an interface: <pre id> and its <template>s
  var cliDefault = {};
  $$("pre.code[data-cli-v]").forEach(function (pre) { cliDefault[pre.id] = pre.textContent; });
  function setCli(preId, v) {
    var pre = $("#" + preId);
    var tpl = $('template[data-cli-template="' + preId + '"][data-cli-v="' + v + '"]');
    pre.textContent = tpl ? tpl.content.textContent : cliDefault[preId];
    pre.dataset.cliV = v;
  }

  // ---------- Variants on the comparison chart and in the tables ----------
  function setVariant(v, on) {
    $$('[data-vt="' + v + '"]').forEach(function (cb) { cb.checked = on; });
    $$('.chart [data-v="' + v + '"]').forEach(function (el) { el.classList.toggle("off", !on); });
    $$('.dtable.diff tr[data-v="' + v + '"], .dtable.series [data-v="' + v + '"]').forEach(function (el) { el.classList.toggle("off", !on); });
    var item = $('.var input[data-vt="' + v + '"]');
    if (item) item.closest(".var").classList.toggle("off", !on);
    var n = $$(".var input[data-vt]:checked").length;
    var meta = $(".var").closest(".step").querySelector(".meta");
    meta.textContent = "6 · " + n + " na wykresie";
  }
  $$("[data-vt]").forEach(function (cb) {
    cb.addEventListener("change", function () { setVariant(cb.dataset.vt, cb.checked); });
  });
  $$(".var").forEach(function (li) {
    li.addEventListener("click", function (e) {
      if (e.target.closest("input")) return;
      var v = li.querySelector("input").dataset.vt;
      var focused = li.classList.toggle("focus");
      $$(".var").forEach(function (x) { if (x !== li) x.classList.remove("focus"); });
      $$(".chart [data-v]").forEach(function (el) {
        el.classList.toggle("dim", focused && el.dataset.v !== v);
      });
      selectTab("hydrogram", "hg-compare");
      showToast(focused ? "Wariant W" + v + " wyróżniony na wykresie porównania" : "Wszystkie warianty bez wyróżnienia");
    });
  });

  // ---------- Explanations (i) and menus ----------
  var openPop = null;
  var openPopBtn = null;
  var openMenu = null;

  function place(el, anchor, prefer) {
    var r = anchor.getBoundingClientRect();
    var w = el.offsetWidth;
    var h = el.offsetHeight;
    var left;
    var top;
    if (prefer === "below") {
      left = Math.min(r.left, window.innerWidth - w - 12);
      top = r.bottom + 6;
      if (top + h > window.innerHeight - 12) top = Math.max(12, r.top - h - 6);
    } else {
      // Beside the panel that holds the anchor, over the charts, so the form stays visible
      var holder = anchor.closest(".view-panel");
      var box = holder ? holder.getBoundingClientRect() : r;
      var onRight = holder && holder.classList.contains("right");
      left = onRight ? box.left - w - 12 : box.right + 12;
      if (left + w > window.innerWidth - 12) left = r.left - w - 12;
      if (left < 12) left = Math.max(12, (window.innerWidth - w) / 2);
      top = Math.min(Math.max(12, r.top - 48), window.innerHeight - h - 12);
    }
    el.style.left = Math.max(12, left) + "px";
    el.style.top = Math.max(12, top) + "px";
  }
  function closePop() {
    if (!openPop) return;
    openPop.hidden = true;
    if (openPopBtn) openPopBtn.setAttribute("aria-expanded", "false");
    openPop = null;
    openPopBtn = null;
  }
  function openInfo(id, btn) {
    var pop = $("#" + id);
    if (openPop === pop) { closePop(); return; }
    closeFloating();
    pop.hidden = false;
    place(pop, btn, "side");
    openPop = pop;
    openPopBtn = btn;
    if (btn.classList.contains("info-btn")) btn.setAttribute("aria-expanded", "true");
    $(".ip-head .btn", pop).focus({ preventScroll: true });
  }
  $$("[data-info]").forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      openInfo(b.dataset.info, b);
    });
  });
  $$("[data-info-close]").forEach(function (b) {
    b.addEventListener("click", function () {
      var back = openPopBtn;
      closePop();
      if (back) back.focus();
    });
  });

  function closeMenu() {
    if (!openMenu) return;
    openMenu.menu.hidden = true;
    openMenu.btn.setAttribute("aria-expanded", "false");
    openMenu = null;
  }
  function toggleMenu(id, btn) {
    var menu = $("#" + id);
    if (openMenu && openMenu.menu === menu) { closeMenu(); return; }
    closeFloating();
    menu.hidden = false;
    place(menu, btn, "below");
    btn.setAttribute("aria-expanded", "true");
    openMenu = { menu: menu, btn: btn };
    $("button", menu).focus({ preventScroll: true });
  }
  function closeFloating() {
    closePop();
    closeMenu();
  }
  $$("[data-menu]").forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      toggleMenu(b.dataset.menu, b);
    });
  });
  document.addEventListener("click", function (e) {
    if (openPop && !openPop.contains(e.target)) closePop();
    if (openMenu && !openMenu.menu.contains(e.target)) closeMenu();
  });

  // ---------- Actions that depend on the host ----------
  $$('[data-action="load-hydrograf"]').forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      if (root.dataset.host === "nogat") showToast("Wczytano zlewnię zaznaczoną w Hydrografie (nogat-handoff/1, przez powłokę)");
      else toggleMenu("menu-load", b);
    });
  });
  $$('[data-action="pmaxtp"]').forEach(function (b) {
    b.addEventListener("click", function () {
      showToast(root.dataset.host === "nogat"
        ? "Moduł IMGWTools: PMAXTP p 1%, 12 h = 105,0 mm"
        : "Samodzielnie: wklej wynik imgw pmaxtp fetch albo wpisz wysokość ręcznie");
    });
  });

  // ---------- Toasts and copying ----------
  $$("[data-toast]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      if (el.tagName === "A") e.preventDefault();
      showToast(el.dataset.toast);
      if (el.closest(".menu")) closeMenu();
    });
  });
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand("copy"); } catch (err) { ok = false; }
      document.body.removeChild(ta);
      if (ok) resolve(); else reject(new Error("copy"));
    });
  }
  $$("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      copyText($("#" + b.dataset.copy).textContent).then(
        function () { showToast("Skopiowano do schowka"); },
        function () { showToast("Nie udało się skopiować: zaznacz tekst i skopiuj ręcznie"); }
      );
    });
  });

  // ---------- Searchable command lists ----------
  function fold(s) {
    return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/ł/g, "l");
  }
  $$("[data-cmd-filter]").forEach(function (tools) {
    var key = tools.dataset.cmdFilter;
    var list = $('[data-cmd-list="' + key + '"]');
    var select = $("[data-cmd-group]", tools);
    var input = $("[data-cmd-search]", tools);
    var items = $$(".cmd-item", list);
    items.forEach(function (it) { it.dataset.hay = fold(it.textContent + " " + (it.dataset.k || "")); });
    function apply() {
      var g = select.value;
      var words = fold(input.value).split(/\s+/).filter(Boolean);
      var shown = {};
      var count = 0;
      items.forEach(function (it) {
        var ok = (!g || it.dataset.g === g) && words.every(function (w) { return it.dataset.hay.indexOf(w) >= 0; });
        it.hidden = !ok;
        if (ok) { shown[it.dataset.g] = true; count++; }
      });
      $$(".cmd-group", list).forEach(function (h) { h.hidden = !shown[h.dataset.g]; });
      $(".cmd-empty", list).hidden = count > 0;
    }
    // The selected command is in view when the section opens
    function revealActive() {
      var act = $(".cmd-item.active", list);
      if (act && !act.hidden && list.clientHeight) list.scrollTop = Math.max(0, act.offsetTop - list.clientHeight / 3);
    }
    reveals.push(revealActive);
    select.addEventListener("change", apply);
    input.addEventListener("input", apply);
    items.forEach(function (it) {
      $("button", it).addEventListener("click", function () {
        if (it.classList.contains("active")) return;
        items.forEach(function (x) { x.classList.toggle("active", x === it); });
        var name = $("code", it) ? $("code", it).textContent : $("strong", it).textContent;
        var view = tools.closest(".view-layout");
        if ($('[data-cmd="' + name + '"]', view)) showCommand(view, name);
        else showToast("Makieta: formularz „" + name + "” powstaje z katalogu tak jak uh nash i scs effective");
      });
    });
  });

  // A command of the catalog shown in the form, the result and the calls
  function showCommand(view, name) {
    $$("[data-cmd]", view).forEach(function (el) { el.hidden = el.dataset.cmd !== name; });
    var formEl = activeForm();
    if (formEl) runBtn.setAttribute("form", formEl.id);
    view.dataset.context = name + " · 44 polecenia w 15 grupach";
    $$(".crumb-context").forEach(function (el) { el.textContent = view.dataset.context; });
    document.title = "Hydrolog: " + view.dataset.title + " — " + view.dataset.context;
    validateForm();
  }

  // ---------- Catalog forms (uh nash, scs effective): bounds and rules from the catalog ----------
  var runBtn = $("#pc-run");
  var formState = $("#pc-state");
  function activeForm() {
    return $("#view-polecenia .cmd-panel:not([hidden]) form");
  }
  function num(s) {
    s = s.trim().replace(/\s/g, "").replace(",", ".");
    if (s === "") return null;
    var v = Number(s);
    return isFinite(v) ? v : NaN;
  }
  function pl(v) { return String(v).replace(".", ","); }
  function checkOpt(opt) {
    var input = $(".ibox input", opt);
    if (!input) return true;
    var err = $(".err", opt);
    var v = num(input.value);
    var d = input.dataset;
    var msg = "";
    if (v === null) {
      if ($(".req", opt)) msg = "Podaj wartość: opcja wymagana · missing";
    } else if (isNaN(v)) {
      msg = "Podaj liczbę, np. 14,78 · type";
    } else if (d.xmin != null && !(v > Number(d.xmin))) {
      msg = "Musi być większa od " + pl(d.xmin) + " (podano " + pl(v) + ") · exclusive_minimum";
    } else if (d.min != null && v < Number(d.min)) {
      msg = "Najmniej " + pl(d.min) + " (podano " + pl(v) + ") · minimum";
    } else if (d.max != null && v > Number(d.max)) {
      msg = "Najwyżej " + pl(d.max) + " (podano " + pl(v) + ") · maximum";
    } else if (d.le) {
      var ref = num($("#" + d.le).value);
      if (ref !== null && !isNaN(ref) && v > ref) msg = d.leMsg + " (" + pl(ref) + " km)";
    }
    opt.classList.toggle("invalid", !!msg);
    input.setAttribute("aria-invalid", String(!!msg));
    err.textContent = msg;
    err.hidden = !msg;
    return !msg;
  }
  function validateForm() {
    var bad = 0;
    $$(".opt", activeForm()).forEach(function (opt) {
      if (opt.closest(".pane[hidden]")) {
        opt.classList.remove("invalid");
        if ($(".err", opt)) $(".err", opt).hidden = true;
        return;
      }
      if (!checkOpt(opt)) bad++;
    });
    runBtn.disabled = bad > 0;
    formState.textContent = bad ? (bad === 1 ? "1 błąd: popraw pole oznaczone na czerwono" : bad + " błędy: popraw pola oznaczone na czerwono") : "formularz poprawny";
  }
  var RUN_TOAST = {
    "pc-form": "Makieta: uh nash obliczył 152 rzędne (n 3,631, K 82,35 min)",
    "pc-form-scs": "Makieta: scs effective dał Pe = 28,12 mm z 72 kroków opadu"
  };
  $$("#view-polecenia .cmd-panel form").forEach(function (f) {
    $$(".opt .ibox input", f).forEach(function (i) { i.addEventListener("input", validateForm); });
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      validateForm();
      if (!runBtn.disabled) showToast(RUN_TOAST[f.id]);
    });
  });

  // ---------- Network nodes: list and schematic ----------
  var NODE_FORM = { ZB: 2, R1: 3 };   // index of the node's step in the Dane panel of Sieć
  function selectNode(id) {
    $$("[data-node]").forEach(function (el) { el.classList.toggle("sel", el.dataset.node === id); });
    var steps = $$('.view-layout[data-section="siec"] .view-panel.left .step');
    if (NODE_FORM[id] != null) {
      var step = steps[NODE_FORM[id]];
      step.open = true;
      step.scrollIntoView({ block: "nearest", behavior: "smooth" });
    } else {
      showToast("Makieta: formularze mają węzły ZB i R1; " + id + " pokazuje dane i wynik tak samo");
    }
  }
  $$("[data-node]").forEach(function (el) {
    el.addEventListener("click", function () { selectNode(el.dataset.node); });
    el.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); selectNode(el.dataset.node); }
    });
  });

  // ---------- Status of the result: current, or stale after the data changed ----------
  var stale = {};
  function renderStatus() {
    var isStale = !!stale[activeView().dataset.section];
    $$(".badge.status").forEach(function (b) {
      b.classList.toggle("ok", !isStale);
      b.classList.toggle("warn", isStale);
      $(".label", b).textContent = isStale ? "Dane zmienione: oblicz ponownie" : "Wynik aktualny";
      b.title = isStale ? "Wyniki odpowiadają poprzednim danym" : "Wyniki odpowiadają danym w panelu Dane";
    });
  }
  function markStale(el) {
    stale[el.closest(".view-layout").dataset.section] = true;
    renderStatus();
  }
  $$(".view-panel.left").forEach(function (p) {
    function onEdit(e) {
      if (e.target.matches("[data-vt], [data-cmd-search], [data-cmd-group]")) return;
      if (e.target.matches("input, select")) markStale(e.target);
    }
    p.addEventListener("input", onEdit);
    p.addEventListener("change", onEdit);
    $$(".seg[role='radiogroup'] button", p).forEach(function (b) {
      b.addEventListener("click", function () { markStale(b); });
    });
  });
  $$(".panel-foot .btn.primary").forEach(function (b) {
    b.addEventListener("click", function () {
      if (b.disabled) return;
      stale[b.closest(".view-layout").dataset.section] = false;
      renderStatus();
    });
  });

  // ---------- Keyboard ----------
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (openPop || openMenu) {
      var back = openPop ? openPopBtn : openMenu.btn;
      closeFloating();
      if (back) back.focus();
      return;
    }
    if (phone.matches && state.sheet) closePanel(state.sheet);
  });
  window.addEventListener("resize", function () { closeFloating(); });

  // ---------- Initial state ----------
  showSection(sectionFromHash());
  validateForm();
})();
