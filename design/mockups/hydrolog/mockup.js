// Hydrolog mockup interactions: theme, host mode (alone or in Nogat's shell), sections of the
// rail, panels and phone sheets, resizers, segmented controls and their panes, the Hydrogram
// results that follow every change, the network nodes and their settings, explanations (i),
// menus, searchable command lists, validation of the catalog form, copying commands and toasts.
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
  // Select lists that switch panes (the settings of a network node)
  $$("select[data-panes]").forEach(function (sel) {
    sel.addEventListener("change", function () {
      $$('.pane[data-group="' + sel.dataset.panes + '"]').forEach(function (p) { p.hidden = p.dataset.pane !== sel.value; });
    });
  });

  // Command shown for an interface of a catalog command: <pre id> and its <template>s
  var cliDefault = {};
  $$("pre.code[data-cli-v]").forEach(function (pre) { cliDefault[pre.id] = pre.textContent; });
  function setCli(preId, v) {
    var pre = $("#" + preId);
    var tpl = $('template[data-cli-template="' + preId + '"][data-cli-v="' + v + '"]');
    pre.textContent = tpl ? tpl.content.textContent : cliDefault[preId];
    pre.dataset.cliV = v;
  }

  // ---------- Hydrogram zlewni: the results follow every change of the data ----------
  // No compute button: each change shows "Liczenie…" and then the result. Every result shown is
  // a real `hydrograph generate` run (#hg-data): 6 tc methods x AMC I-III x 4 UH models.
  var HG = JSON.parse($("#hg-data").textContent);
  var hgView = $("#view-hydrogram");
  var hgLeft = $(".view-panel.left", hgView);
  var NB = "\u00a0";
  var TC_NAME = { kirpich: "Kirpich", nrcs: "NRCS", giandotti: "Giandotti", faa: "FAA", kerby: "Kerby", kerby_kirpich: "Kerby–Kirpich" };
  var TC_HINT = {
    kirpich: "Wzór Kirpicha (domyślny): z długości i spadku cieku głównego.",
    nrcs: "NRCS (TR-55): z długości, spadku zlewni i CN.",
    giandotti: "Giandotti: z powierzchni, długości i wysokości zlewni.",
    faa: "FAA: tylko spływ po stoku (długość, spadek, C).",
    kerby: "Kerby: tylko spływ po stoku (długość, spadek, retardacja N).",
    kerby_kirpich: "Kerby–Kirpich: stok (Kerby) i koryto (Kirpich)."
  };
  var UH_NAME = { scs: "SCS", nash: "Nash", clark: "Clark", snyder: "Snyder" };
  var hgBusy = false;
  var hgTimer = 0;
  var hgDebounce = 0;
  var hgShown = "";

  function fmt(v, d) {
    var parts = Math.abs(v).toFixed(d).split(".");
    var ip = parts[0].length >= 5 ? parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, NB) : parts[0];
    return (v < 0 ? "−" : "") + ip + (parts[1] ? "," + parts[1] : "");
  }
  function hmm(m) { m = Math.round(m); return Math.floor(m / 60) + ":" + String(m % 60).padStart(2, "0"); }
  function c1(v) { return String(Math.round(v * 10) / 10); }
  function pts(list) { return list.map(function (p) { return c1(p[0]) + "," + c1(p[1]); }).join(" "); }
  function nice(max, ticks) {
    var steps = [0.5, 1, 2, 5, 10, 20, 25, 50, 100];
    for (var i = 0; i < steps.length; i++) {
      var top = Math.ceil(max * 1.08 / steps[i]) * steps[i];
      if (top / steps[i] <= ticks) return { top: top, step: steps[i] };
    }
    return { top: max, step: max };
  }
  function range(top, step) {
    var out = [];
    for (var v = 0; v <= top + 1e-9; v += step) out.push(Math.round(v * 1e6) / 1e6);
    return out;
  }
  function gridH(ys, x0, x1) {
    return '<g class="grid">' + ys.map(function (y) { return '<line x1="' + x0 + '" x2="' + x1 + '" y1="' + c1(y) + '" y2="' + c1(y) + '"/>'; }).join("") + "</g>";
  }
  function text(cls, x, y, s, anchor) {
    return '<text class="' + cls + '" x="' + c1(x) + '" y="' + c1(y) + '"' + (anchor ? ' text-anchor="' + anchor + '"' : "") + ">" + s + "</text>";
  }
  function usesTc(uh) { return uh === "scs" || uh === "clark"; }
  function scenarioKey(st) { return st.uh + "|" + (usesTc(st.uh) ? st.tc : "-") + "|" + st.amc; }

  // Hyetograph on top (inverted) and hydrograph below, on one time axis
  function chartMain(s, pe, ia) {
    var P = HG.p, X0 = 56, X1 = 744, TOP = 26, PB = 118, QT = 146, QB = 394;
    var kp = (PB - TOP) / 4, sc = nice(s.qmax, 7), kq = (QB - QT) / sc.top;
    function xt(t) { return X0 + (X1 - X0) * t / 1440; }
    var o = ['<svg viewBox="0 0 760 432" role="img" aria-labelledby="hg-chart-title" class="chart-svg">'];
    o.push(gridH([0, 1, 2, 3, 4].map(function (v) { return TOP + v * kp; }), X0, X1));
    o.push(gridH(range(sc.top, sc.step).map(function (v) { return QB - v * kq; }), X0, X1));
    var hours = range(24, 2);
    o.push('<g class="grid v">' + hours.map(function (h) { var x = c1(xt(h * 60)); return '<line x1="' + x + '" x2="' + x + '" y1="' + TOP + '" y2="' + QB + '"/>'; }).join("") + "</g>");
    var w = c1(xt(10) - xt(0) - 1), bp = "", be = "";
    P.forEach(function (p, k) {
      var x = c1(xt(k * 10) + 0.5);
      bp += '<rect x="' + x + '" y="' + TOP + '" width="' + w + '" height="' + c1(p * kp) + '"/>';
      if (pe[k] > 0) be += '<rect x="' + x + '" y="' + TOP + '" width="' + w + '" height="' + c1(pe[k] * kp) + '"/>';
    });
    o.push('<g class="bar-p">' + bp + '</g><g class="bar-pe">' + be + "</g>");
    var first = pe.findIndex(function (v) { return v > 0; });
    var xs = xt(first * 10);
    o.push('<line class="mark-line" x1="' + c1(xs) + '" x2="' + c1(xs) + '" y1="' + TOP + '" y2="' + (PB + 8) + '"/>');
    o.push(text("note", xs + 5, PB + 6, "Pe &gt; 0 od " + hmm(first * 10) + " (Ia = " + fmt(ia, 1) + " mm)"));
    var kmax = 0;
    P.forEach(function (p, k) { if (p > P[kmax]) kmax = k; });
    o.push(text("note", xt(kmax * 10 + 10) + 6, TOP + P[kmax] * kp - 4,
      "Pmax " + fmt(P[kmax], 2) + " mm / 10 min · " + hmm(kmax * 10) + "–" + hmm(kmax * 10 + 10)));
    var line = s.q.map(function (q, i) { return [xt(i * 10), QB - q * kq]; });
    o.push('<path class="q-area s1" d="M' + pts([[X0, QB]].concat(line, [[X1, QB]])) + ' Z"/>');
    o.push('<polyline class="ser s1" points="' + pts(line) + '"/>');
    var px = xt(s.tp), py = QB - s.qmax * kq, bx = px + 214 > X1 ? px - 202 : px + 12;
    o.push('<line class="peak-line" x1="' + c1(px) + '" x2="' + c1(px) + '" y1="' + c1(py) + '" y2="' + QB + '"/>');
    o.push('<circle class="peak-dot s1" cx="' + c1(px) + '" cy="' + c1(py) + '" r="4.5"/>');
    o.push('<rect class="peak-box" x="' + c1(bx) + '" y="' + c1(py - 15) + '" width="190" height="22" rx="4"/>');
    o.push(text("peak-label", bx + 8, py, "Qmax " + fmt(s.qmax, 1) + " m³/s · " + hmm(s.tp) + " h"));
    o.push('<line class="axis" x1="' + X0 + '" x2="' + X1 + '" y1="' + TOP + '" y2="' + TOP + '"/>');
    o.push('<line class="axis" x1="' + X0 + '" x2="' + X1 + '" y1="' + QB + '" y2="' + QB + '"/>');
    [0, 1, 2, 3, 4].forEach(function (v) { o.push(text("tick", X0 - 6, TOP + v * kp + 3, v, "end")); });
    range(sc.top, sc.step).forEach(function (v) { o.push(text("tick", X0 - 6, QB - v * kq + 3, fmt(v, 0), "end")); });
    hours.forEach(function (h) { o.push(text("tick", xt(h * 60), QB + 15, h, "middle")); });
    o.push(text("axis-label", X1, QB + 32, "czas [h]", "end"));
    o.push(text("axis-label", 4, 14, "P, Pe [mm / 10 min]"));
    o.push(text("axis-label", 4, QT - 8, "Q [m³/s]"));
    return o.join("") + "</svg>";
  }

  // Cumulative rain, initial abstraction and effective rain over the rain duration
  function chartCum(a) {
    var x0 = 40, x1 = 350, y0 = 150, y1 = 12;
    function sx(t) { return x0 + (x1 - x0) * t / 720; }
    function sy(v) { return y0 - (y0 - y1) * v / 120; }
    var cp = [[x0, y0]], ce = [[x0, y0]], sp = 0, se = 0;
    HG.p.forEach(function (p, k) {
      sp += p;
      se += a.pe[k];
      cp.push([sx((k + 1) * 10), sy(sp)]);
      ce.push([sx((k + 1) * 10), sy(se)]);
    });
    var first = a.pe.findIndex(function (v) { return v > 0; });
    var o = ['<svg viewBox="0 0 360 178" role="img" aria-labelledby="hg-cum-title">'];
    o.push(gridH(range(120, 30).map(sy), x0, x1));
    o.push('<path class="q-area s1" d="M' + pts(ce.concat([[x1, y0]])) + ' Z"/>');
    o.push('<polyline class="ser s1" points="' + pts(ce) + '"/>');
    o.push('<polyline class="ser s4" points="' + pts(cp) + '"/>');
    o.push('<line class="peak-line" x1="' + x0 + '" x2="' + x1 + '" y1="' + c1(sy(a.ia)) + '" y2="' + c1(sy(a.ia)) + '"/>');
    o.push(text("peak-tag", x1 - 2, sy(a.ia) - 4, "Ia = " + fmt(a.ia, 1) + " mm", "end"));
    o.push('<line class="mark-line" x1="' + c1(sx(first * 10)) + '" x2="' + c1(sx(first * 10)) + '" y1="' + c1(sy(a.ia)) + '" y2="' + y0 + '"/>');
    o.push(text("peak-tag", sx(first * 10) + 5, y0 - 6, hmm(first * 10)));
    o.push(text("peak-tag", x1 - 2, sy(sp) + 14, "P = " + fmt(sp, 1) + " mm", "end"));
    o.push(text("peak-tag", x1 - 2, sy(se) - 6, "Pe = " + fmt(se, 1) + " mm", "end"));
    o.push('<line class="axis" x1="' + x0 + '" x2="' + x1 + '" y1="' + y0 + '" y2="' + y0 + '"/>');
    range(120, 30).forEach(function (v) { o.push(text("tick", x0 - 6, sy(v) + 3, v, "end")); });
    range(12, 2).forEach(function (h) { o.push(text("tick", sx(h * 60), 164, h, "middle")); });
    o.push(text("axis-label", x1, 177, "czas [h]", "end"));
    o.push(text("axis-label", 4, 6, "suma [mm]"));
    return o.join("") + "</svg>";
  }

  // Unit hydrograph of the chosen model (the same one the hydrograph convolves)
  function chartUH(u) {
    var x0 = 40, x1 = 350, y0 = 150, y1 = 12, last = 0;
    u.u.forEach(function (v, i) { if (v > u.qp * 0.01) last = i; });
    var th = Math.min(24, Math.max(3, Math.ceil((last + 1) * 10 / 60)));
    var every = th <= 9 ? 1 : th <= 18 ? 2 : 3;
    var sc = nice(u.qp, 6);
    function sx(t) { return x0 + (x1 - x0) * t / (th * 60); }
    function sy(q) { return y0 - (y0 - y1) * q / sc.top; }
    var line = [];
    u.u.forEach(function (v, i) { if (i * 10 <= th * 60) line.push([sx(i * 10), sy(v)]); });
    var o = ['<svg viewBox="0 0 360 178" role="img" aria-labelledby="hg-uh-title">'];
    o.push(gridH(range(sc.top, sc.step).map(sy), x0, x1));
    o.push('<path class="q-area s1" d="M' + pts([[line[0][0], y0]].concat(line, [[line[line.length - 1][0], y0]])) + ' Z"/>');
    o.push('<polyline class="ser s1" points="' + pts(line) + '"/>');
    var px = sx(u.tp), py = sy(u.qp), right = px > 240;
    o.push('<circle class="peak-dot s1" cx="' + c1(px) + '" cy="' + c1(py) + '" r="3.5"/>');
    o.push(text("peak-tag", right ? px - 7 : px + 7, py - 5, "qp " + fmt(u.qp, 2) + " · tp " + hmm(u.tp), right ? "end" : null));
    o.push('<line class="axis" x1="' + x0 + '" x2="' + x1 + '" y1="' + y0 + '" y2="' + y0 + '"/>');
    range(sc.top, sc.step).forEach(function (v) { o.push(text("tick", x0 - 6, sy(v) + 3, fmt(v, sc.step < 1 ? 1 : 0), "end")); });
    range(th, every).forEach(function (h) { o.push(text("tick", sx(h * 60), 164, h, "middle")); });
    o.push(text("axis-label", x1, 177, "czas [h]", "end"));
    o.push(text("axis-label", 4, 6, "u [m³/s na 1 mm]"));
    return o.join("") + "</svg>";
  }

  function seriesRows(s, pe) {
    var rows = [];
    for (var i = 0; i < s.q.length; i++) {
      var t = i * 10, k = i - 1;
      var p = k >= 0 && k < HG.p.length ? fmt(HG.p[k], 2) : "–";
      var e = k >= 0 && k < pe.length ? fmt(pe[k], 2) : "–";
      rows.push("<tr" + (t === s.tp ? ' class="peak"' : "") + '><th scope="row">' + hmm(t) + '</th><td class="t">' + t +
        "</td><td>" + p + "</td><td>" + e + "</td><td>" + fmt(s.q[i], 2) + "</td></tr>");
    }
    return rows.join("");
  }

  var ICON = {
    warn: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2l6.5 11.5h-13z"/><path d="M8 6.5v3.2M8 11.7v.01"/></svg>',
    ok: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5"/><path d="M5 8.2l2 2 4-4.2"/></svg>',
    info: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5"/><path d="M8 7.5v4M8 5v.01"/></svg>'
  };
  var LEVEL = { warn: "Uwaga", ok: "W zakresie", info: "Informacja" };
  function noteItem(kind, body, from) {
    return '<li class="' + kind + '">' + ICON[kind] + '<div><span class="lvl">' + LEVEL[kind] + "</span> " + body + '<span class="from">' + from + "</span></div></li>";
  }
  // Applicability checks of the GUI, then Hydrolog's own notices
  function notesFor(st, s, u) {
    var out = [];
    if (!usesTc(st.uh)) {
      out.push(noteItem("info", "Model " + UH_NAME[st.uh] + " nie używa tc: metoda tc nie zmienia wyniku.", "opis <code>uh_model</code> · Hydrolog"));
    } else if (st.tc === "kirpich") {
      out.push(noteItem("warn", "Kirpich: zlewnia 37,22 km² leży poza zakresem danych wzoru (małe zlewnie rolnicze 0,004–0,45 km²); L i S mieszczą się w progach Hydrologu.",
        'zakres metody · <button class="link-btn" type="button" data-info="info-kirpich">objaśnienie</button>'));
    } else if (st.tc === "nrcs") {
      out.push(noteItem("ok", "NRCS (TR-55): L 14,78 km, S 0,0142 m/m i CN 65 w zakresie metody (L 0,03–30 km, S 0,001–0,15, CN 50–95).", "zakres metody"));
    } else if (st.tc === "faa" || st.tc === "kerby") {
      out.push(noteItem("warn", TC_NAME[st.tc] + " liczy tylko spływ po stoku (0,30 km): dla zlewni 37,22 km² z korytem 14,78 km tc wychodzi kilkakrotnie za krótki. Użyj Kerby–Kirpich albo Kirpicha.", "zakres metody"));
    }
    s.notices.forEach(function (n) { out.push(noteItem("warn", n, "<code>user_warning</code> · hydrograph generate")); });
    out.push(noteItem("ok", "SCS-CN: A = 37,22 km² nie przekracza 250 km² i zalecenia NEH 630 dla jednorodnej zlewni (ok. 52 km²).",
      'zakres metody · <button class="link-btn" type="button" data-info="info-scs">objaśnienie</button>'));
    var lim = 0.25 * u.tp;
    out.push(lim >= 10
      ? noteItem("ok", "Krok Δt = 10 min ≤ 0,25·t<sub>p</sub> hydrogramu jednostkowego (" + fmt(lim, 1) + " min).", "zakres metody")
      : noteItem("warn", "Krok Δt = 10 min &gt; 0,25·t<sub>p</sub> = " + fmt(lim, 1) + " min: hydrogram jednostkowy ma za mało rzędnych przed szczytem; zmniejsz krok.", "zakres metody"));
    if (!s.notices.length) out.push(noteItem("info", "Hydrolog nie zgłosił uwag do tego obliczenia (<code>notices</code>: 0).", "Hydrolog"));
    return out.join("");
  }

  function chip(s) { return '<span class="chip">' + s + "</span>"; }
  function prow(label, sym, v, unit) {
    return "<tr><th>" + label + (sym ? '<span class="sym">' + sym + "</span>" : "") + "</th><td>" + v + '</td><td class="u">' + unit + "</td></tr>";
  }
  function uhParams(st, s, u) {
    if (st.uh === "scs") return [["Opóźnienie UH", "t<sub>lag</sub> = 0,6·tc", fmt(u.lag, 1), "min"]];
    if (st.uh === "clark") return [["Stała retencji", "R = 0,5·tc", fmt(s.r_min, 1), "min"]];
    if (st.uh === "nash") return [["Liczba zbiorników (Lutz)", "n", "3,631", "–"], ["Stała magazynowania (Lutz)", "K", "82,35", "min"]];
    return [["Współczynnik czasowy", "Ct", "1,5", "–"], ["Współczynnik szczytowy", "Cp", "0,6", "–"]];
  }
  function hgSet(name, html) { $('[data-hg="' + name + '"]', hgView).innerHTML = html; }
  function hgText(name, s) { $('[data-hg="' + name + '"]', hgView).textContent = s; }

  function renderHydrogram(st) {
    var s = HG.s[scenarioKey(st)], a = HG.amc[st.amc], u = HG.uh[s.uh], tc = HG.tc[st.tc];
    var label = UH_NAME[st.uh] + (usesTc(st.uh) ? " · " + TC_NAME[st.tc] : "") + " · AMC " + st.amc;
    // Dane: what each step gives
    hgText("tc-meta", usesTc(st.uh) ? fmt(tc, 1) + " min · " + TC_NAME[st.tc] : "nieużywany · " + UH_NAME[st.uh]);
    hgText("tc-v", fmt(tc, 1) + " min");
    hgText("tc-u", "= " + fmt(tc / 60, 2) + " h" + (usesTc(st.uh) ? "" : " · model " + UH_NAME[st.uh] + " go nie używa"));
    hgText("tc-hint", TC_HINT[st.tc]);
    hgText("loss-meta", "CN " + a.cn + " · AMC " + st.amc);
    hgSet("loss-chips", chip("CN " + a.cn + (st.amc === "II" ? "" : " (65 → AMC " + st.amc + ")")) + chip("S = " + fmt(a.s, 1) + " mm") + chip("Ia = λ·S = " + fmt(a.ia, 1) + " mm"));
    hgText("uh-meta", UH_NAME[st.uh]);
    hgSet("uh-chips", uhParams(st, s, u).map(function (r) { return chip(r[1] + " = " + r[2] + (r[3] === "–" ? "" : " " + r[3])); }).join("") +
      chip("t<sub>p</sub> = " + fmt(u.tp, 1) + " min") + chip("q<sub>p</sub> = " + fmt(u.qp, 2) + " m³/s na 1 mm"));
    // Charts and table
    hgText("chart-sub", label + " · PMAXTP p 1%, 12 h, Beta (2; 5) · Δt 10 min");
    hgSet("chart-main", chartMain(s, a.pe, a.ia));
    hgSet("chart-cum", chartCum(a));
    hgText("uh-title", "Hydrogram jednostkowy " + UH_NAME[st.uh]);
    hgText("uh-cmd", "uh " + st.uh);
    hgSet("chart-uh", chartUH(u));
    hgSet("series", seriesRows(s, a.pe));
    hgText("series-note", "Q w m³/s. Wiersz szczytu (" + hmm(s.tp) + ") wyróżniony.");
    // Wyniki
    hgText("res-sub", label);
    hgText("k-q", fmt(s.qmax, 1));
    hgText("k-tp", hmm(s.tp));
    hgText("k-v", fmt(s.v / 1e6, 3));
    hgText("k-c", fmt(a.c, 3));
    hgSet("notes", notesFor(st, s, u));
    var P = 105, f = P - a.ia - a.pe_total;
    function pct(v) { return fmt(v / P * 100, 1) + " %"; }
    var wi = a.ia / P * 100, wf = f / P * 100;
    hgText("bal-meta", "C = Pe / P = " + fmt(a.c, 3));
    hgSet("bal-stack", '<svg class="stack" viewBox="0 0 100 1" preserveAspectRatio="none" role="img" aria-label="Podział opadu: Ia ' + pct(a.ia) + ", F " + pct(f) + ", Pe " + pct(a.pe_total) + '">' +
      '<rect class="b-ia" x="0" y="0" width="' + wi.toFixed(2) + '" height="1"/><rect class="b-f" x="' + wi.toFixed(2) + '" y="0" width="' + wf.toFixed(2) + '" height="1"/>' +
      '<rect class="b-pe" x="' + (wi + wf).toFixed(2) + '" y="0" width="' + (100 - wi - wf).toFixed(2) + '" height="1"/></svg>');
    hgSet("bal-rows",
      '<tr><th>Opad całkowity<span class="sym">P</span></th><td>' + fmt(P, 2) + '</td><td class="u">mm</td><td class="pct">100 %</td></tr>' +
      '<tr><th><i class="dot b-ia"></i>Abstrakcja początkowa<span class="sym">Ia</span></th><td>' + fmt(a.ia, 2) + '</td><td class="u">mm</td><td class="pct">' + pct(a.ia) + "</td></tr>" +
      '<tr><th><i class="dot b-f"></i>Infiltracja<span class="sym">F</span></th><td>' + fmt(f, 2) + '</td><td class="u">mm</td><td class="pct">' + pct(f) + "</td></tr>" +
      '<tr><th><i class="dot b-pe"></i>Opad efektywny<span class="sym">Pe</span></th><td>' + fmt(a.pe_total, 2) + '</td><td class="u">mm</td><td class="pct">' + pct(a.pe_total) + "</td></tr>" +
      '<tr><th>Retencja maksymalna<span class="sym">S</span></th><td>' + fmt(a.s, 2) + '</td><td class="u">mm</td><td class="pct"></td></tr>');
    hgText("bal-note", "Objętość z hydrogramu " + fmt(s.v, 0) + " m³, Pe·A " + fmt(s.vpe, 0) + " m³: różnica " + fmt(Math.abs(s.v - s.vpe) / s.vpe * 100, 2) + " %.");
    var rows = [usesTc(st.uh) ? prow("Czas koncentracji", "tc · " + TC_NAME[st.tc], fmt(tc, 1), "min") : prow("Czas koncentracji", "tc", "nieużywany", ""),
      prow("CN po korekcie AMC", "cn_adjusted", a.cn, "–")];
    uhParams(st, s, u).forEach(function (r) { rows.push(prow(r[0], r[1], r[2], r[3])); });
    rows.push(prow("Czas do szczytu UH", "t<sub>p</sub>", fmt(u.tp, 1), "min"), prow("Szczyt UH", "q<sub>p</sub>", fmt(u.qp, 2), "m³/s/mm"),
      prow("Długość hydrogramu", "", fmt(s.dur, 0), "min"), prow("Krok obliczeń", "Δt", "10", "min"));
    hgSet("params", rows.join(""));
    $("#hg-cli").textContent = s.cli;
  }

  function hgReadState() {
    return {
      tc: $("#hg-tcm").value,
      amc: $('[aria-labelledby="hg-amc-label"] button.on', hgView).textContent.trim(),
      uh: $('[data-panes="hg-uh"] button.on', hgView).dataset.pane
    };
  }
  function renderCalcState() {
    var el = $('[data-hg="state"]', hgView);
    el.classList.toggle("busy", hgBusy);
    $("span", el).textContent = hgBusy ? "Liczenie…" : "Wynik aktualny · liczy się sam po każdej zmianie";
  }
  function setBusy(on) {
    hgBusy = on;
    hgView.classList.toggle("computing", on);
    $$("[data-hg-res]", hgView).forEach(function (el) { if (on) el.setAttribute("aria-busy", "true"); else el.removeAttribute("aria-busy"); });
    renderCalcState();
    renderStatus();
  }
  // A short "Liczenie…" for every change; the result switches when tc method, AMC or UH model changed
  function hgCompute() {
    clearTimeout(hgTimer);
    setBusy(true);
    hgTimer = setTimeout(function () {
      var st = hgReadState(), key = scenarioKey(st);
      if (key !== hgShown) { renderHydrogram(st); hgShown = key; }
      setBusy(false);
    }, 450);
  }
  hgLeft.addEventListener("change", function (e) { if (e.target.matches("select, input[type='checkbox']")) hgCompute(); });
  hgLeft.addEventListener("input", function (e) {
    if (!e.target.matches("input[type='text']")) return;
    clearTimeout(hgDebounce);
    hgDebounce = setTimeout(hgCompute, 400);
  });
  $$(".seg[role='radiogroup'] button, .chg .link-btn", hgLeft).forEach(function (b) { b.addEventListener("click", hgCompute); });
  (function () {
    var st = hgReadState();
    renderHydrogram(st);
    hgShown = scenarioKey(st);
    renderCalcState();
  })();

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
  // Delegated: the notes of the Hydrogram are drawn again with each result
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-info]");
    if (!b) return;
    e.stopImmediatePropagation();
    openInfo(b.dataset.info, b);
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

  // ---------- Sieć: a node selected on the schematic, in the list or the table; its settings in Dane ----------
  var siec = $("#view-siec");
  function selectNode(id, fromSchematic) {
    $$("[data-node]", siec).forEach(function (el) {
      var on = el.dataset.node === id;
      el.classList.toggle("sel", on);
      el.setAttribute("aria-pressed", String(on));
    });
    $$("[data-node-row]", siec).forEach(function (tr) { tr.classList.toggle("sel", tr.dataset.nodeRow === id); });
    var form = null;
    $$("[data-node-form]", siec).forEach(function (f) {
      f.hidden = f.dataset.nodeForm !== id;
      if (!f.hidden) form = f;
    });
    $('[data-nt="title"]', siec).textContent = form.dataset.title;
    $('[data-nt="meta"]', siec).textContent = form.dataset.meta;
    $$("[data-node-res]", siec).forEach(function (b) { b.hidden = b.dataset.nodeRes !== id; });
    $('[data-nt="res-title"]', siec).textContent = "Wybrany węzeł: " + id;
    $('[data-nt="res-sub"]', siec).textContent = "wylot OUT · węzeł " + id;
    var step = $(".node-step", siec);
    step.open = true;
    if (fromSchematic && (phone.matches || !state.open.left)) openPanel("left");
    step.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }
  $$("[data-node]", siec).forEach(function (el) {
    var fromSchematic = !el.closest(".view-panel");
    el.addEventListener("click", function () { selectNode(el.dataset.node, fromSchematic); });
    if (el.tagName === "BUTTON") return;
    el.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); selectNode(el.dataset.node, fromSchematic); }
    });
  });
  $$("[data-node-row]", siec).forEach(function (tr) {
    tr.addEventListener("click", function () { selectNode(tr.dataset.nodeRow, true); });
  });

  // ---------- Status of the result: current, or stale after the data changed ----------
  var stale = {};
  function renderStatus() {
    var section = activeView().dataset.section;
    var busy = section === "hydrogram" && hgBusy;
    var isStale = section !== "hydrogram" && !!stale[section];
    $$(".badge.status").forEach(function (b) {
      b.classList.toggle("ok", !isStale && !busy);
      b.classList.toggle("warn", isStale);
      b.classList.toggle("info", busy);
      $(".label", b).textContent = busy ? "Liczenie…" : isStale ? "Dane zmienione: oblicz ponownie" : "Wynik aktualny";
      b.title = busy ? "Hydrolog liczy wynik dla zmienionych danych"
        : isStale ? "Wyniki odpowiadają poprzednim danym"
        : section === "hydrogram" ? "Wyniki liczą się same po każdej zmianie danych" : "Wyniki odpowiadają danym w panelu Dane";
    });
  }
  function markStale(el) {
    var section = el.closest(".view-layout").dataset.section;
    if (section === "hydrogram") return;   // the Hydrogram recomputes by itself
    stale[section] = true;
    renderStatus();
  }
  $$(".view-panel.left").forEach(function (p) {
    function onEdit(e) {
      if (e.target.matches("[data-cmd-search], [data-cmd-group]")) return;
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
