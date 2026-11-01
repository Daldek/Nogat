// Hydrograf mockup interactions: theme, modes, panels and sheets, resizers, layers, feedback dialog.
(function () {
  "use strict";

  var $ = function (sel) { return document.querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var phone = window.matchMedia("(max-width: 860px)");

  function load(key) {
    try { return JSON.parse(localStorage.getItem(key)); } catch (e) { return null; }
  }
  function save(key, value) {
    try { localStorage.setItem(key, typeof value === "string" ? value : JSON.stringify(value)); } catch (e) {}
  }

  // ---------- Theme ----------
  var THEME_KEY = "nogat-theme";
  var themeButtons = { auto: $("#theme-auto"), light: $("#theme-light"), dark: $("#theme-dark") };

  function setTheme(choice) {
    if (choice === "light" || choice === "dark") document.documentElement.dataset.theme = choice;
    else delete document.documentElement.dataset.theme;
    Object.keys(themeButtons).forEach(function (k) {
      themeButtons[k].setAttribute("aria-pressed", String(k === choice));
    });
  }
  Object.keys(themeButtons).forEach(function (k) {
    themeButtons[k].addEventListener("click", function () {
      save(THEME_KEY, k);
      setTheme(k);
    });
  });
  var storedTheme = null;
  try { storedTheme = localStorage.getItem(THEME_KEY); } catch (e) {}
  setTheme(storedTheme === "light" || storedTheme === "dark" ? storedTheme : "auto");

  // ---------- Panels: desktop columns and phone sheets ----------
  var view = $("#view");
  var panels = { left: $("#left-panel"), right: $("#right-panel") };
  var resizers = { left: $("#left-resizer"), right: $("#right-resizer") };
  var state = {
    mode: "watershed",
    open: { left: true, right: true },            // desktop columns
    sheet: panels.left.classList.contains("open") ? "left" : (panels.right.classList.contains("open") ? "right" : null),
    width: { left: null, right: null }            // null = CSS default
  };

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
    ["left", "right"].forEach(function (side) {
      panels[side].classList.toggle("open", state.sheet === side);
      panels[side].classList.toggle("collapsed", !state.open[side]);
      resizers[side].hidden = !state.open[side];
    });
    $("#open-layers").classList.toggle("show", !state.open.left);
    $(".map-bar .end").classList.toggle("show", !state.open.right);
    $("#open-layers").setAttribute("aria-expanded", String(phone.matches ? state.sheet === "left" : state.open.left));
    $("#open-results").setAttribute("aria-expanded", String(phone.matches ? state.sheet === "right" : state.open.right));
    applyWidths();
  }

  $("#left-close").addEventListener("click", function () { closePanel("left"); });
  $("#right-close").addEventListener("click", function () { closePanel("right"); });
  $("#open-layers").addEventListener("click", function () { togglePanel("left"); });
  $("#open-results").addEventListener("click", function () { togglePanel("right"); });
  $$(".view-panel .grip").forEach(function (grip) {
    grip.addEventListener("click", function () {
      closePanel(grip.closest(".view-panel") === panels.left ? "left" : "right");
    });
  });
  phone.addEventListener("change", render);

  // ---------- Resizers ----------
  var WIDTH_KEY = "hydrograf-mockup-widths";
  var LIMITS = { left: { min: 260, max: 560 }, right: { min: 340, max: 720 } };
  var CENTRE_MIN = 480;
  var other = { left: "right", right: "left" };

  function cssDefault(side) {
    var v = parseInt(getComputedStyle(document.documentElement).getPropertyValue("--" + side + "-w"), 10);
    return isNaN(v) ? LIMITS[side].min : v;
  }
  function ownClamp(side, w) {
    return Math.min(LIMITS[side].max, Math.max(LIMITS[side].min, w));
  }
  function maxFor(side) {
    var o = other[side];
    var otherW = state.open[o] ? ownClamp(o, state.width[o] == null ? cssDefault(o) : state.width[o]) : 0;
    return Math.max(LIMITS[side].min, Math.min(LIMITS[side].max, view.clientWidth - otherW - CENTRE_MIN));
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
      if (phone.matches) { view.style.removeProperty(prop); return; }
      if (!state.open[side]) { view.style.setProperty(prop, "0px"); return; }
      var w = currentWidth(side);
      view.style.setProperty(prop, w + "px");
      resizers[side].setAttribute("aria-valuenow", String(w));
      resizers[side].setAttribute("aria-valuemax", String(maxFor(side)));
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

  ["left", "right"].forEach(function (side) {
    var r = resizers[side];
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

  // ---------- Modes ----------
  var HINTS = {
    browse: "Przesuwaj i przybliżaj mapę",
    watershed: "Kliknij na mapie w pobliżu cieku",
    profile: "Klikaj, aby dodać wierzchołki; dwuklik kończy, Backspace cofa, Esc anuluje"
  };
  var modeButtons = { browse: $("#mode-browse"), watershed: $("#mode-watershed"), profile: $("#mode-profile") };
  var railMap = $("#rail-map");
  var railProfile = $("#rail-profile");
  var mapWrap = $(".map-wrap");

  var ATTRIB = {
    openfreemap: "OpenFreeMap © OpenMapTiles, dane © OpenStreetMap · NMT GUGiK",
    "gugik-osm": "© OpenStreetMap, GUGiK · NMT GUGiK",
    "esri-ortho": "Esri, Maxar, Earthstar Geographics · NMT GUGiK",
    none: "NMT GUGiK"
  };
  document.querySelectorAll('input[name="basemap"]').forEach(function (r) {
    r.addEventListener("change", function () {
      if (!r.checked) return;
      mapWrap.setAttribute("data-basemap", r.value);
      $(".map-attrib").textContent = ATTRIB[r.value];
    });
  });

  function setRail(item) {
    [railMap, railProfile].forEach(function (a) {
      var on = a === item;
      a.classList.toggle("active", on);
      if (on) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
  }

  function setMode(mode) {
    state.mode = mode;
    Object.keys(modeButtons).forEach(function (k) {
      var on = k === mode;
      modeButtons[k].classList.toggle("on", on);
      modeButtons[k].setAttribute("aria-checked", String(on));
      modeButtons[k].tabIndex = on ? 0 : -1;
    });
    $("#map-hint-text").textContent = HINTS[mode];
    mapWrap.dataset.mode = mode;
    $("#profile-drawer").hidden = mode !== "profile";
    setRail(mode === "profile" ? railProfile : railMap);

    if (mode === "browse") closePanel("right");
    else if (mode === "watershed") openPanel("right");
    else if (phone.matches) { state.sheet = null; render(); }  // a sheet would cover the drawer on phones
  }

  Object.keys(modeButtons).forEach(function (k) {
    modeButtons[k].addEventListener("click", function () { setMode(k); });
  });
  railMap.addEventListener("click", function (e) { e.preventDefault(); setMode("watershed"); });
  railProfile.addEventListener("click", function (e) { e.preventDefault(); setMode("profile"); });
  $("#profile-close").addEventListener("click", function () { setMode("watershed"); });
  $$('a[href="#"]').forEach(function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); });
  });

  // ---------- Segmented radio groups (results panel + arrow keys everywhere) ----------
  function selectSeg(btn) {
    var group = btn.closest(".seg");
    $$("button", group).forEach(function (b) {
      var on = b === btn;
      b.classList.toggle("on", on);
      b.setAttribute("aria-checked", String(on));
      b.tabIndex = on ? 0 : -1;
    });
    if (group.id === "dist-seg") $("#beta-params").hidden = btn.textContent.trim() !== "Beta";
  }
  $$("#right-panel .seg[role='radiogroup'] button").forEach(function (b) {
    b.addEventListener("click", function () { selectSeg(b); });
  });
  $$(".seg[role='radiogroup']").forEach(function (group) {
    var buttons = $$("button", group);
    buttons.forEach(function (b) { b.tabIndex = b.getAttribute("aria-checked") === "true" ? 0 : -1; });
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

  // ---------- Layers ----------
  $$(".layer").forEach(function (row) {
    var cb = row.querySelector("input[type='checkbox']");
    var range = row.querySelector("input[type='range']");
    var val = row.querySelector(".val");
    var targets = cb.dataset.layer ? $$(".map-svg [data-layer='" + cb.dataset.layer + "']") : [];
    function apply() {
      row.classList.toggle("off", !cb.checked);
      val.textContent = range.value + "%";
      targets.forEach(function (el) {
        el.style.display = cb.checked ? "" : "none";
        el.style.opacity = String(range.value / 100);
      });
    }
    cb.addEventListener("change", apply);
    range.addEventListener("input", apply);
    apply();
  });

  // ---------- Feedback dialog and toast ----------
  var modal = $("#feedback-modal");
  var form = $("#feedback-form");
  var message = $("#feedback-message");
  var counter = $("#feedback-counter");
  var toast = $("#toast");
  var toastTimer = 0;
  var returnFocus = null;

  function updateCounter() { counter.textContent = message.value.length + "/5000"; }
  function openModal() {
    returnFocus = document.activeElement;
    modal.hidden = false;
    message.focus();
  }
  function closeModal() {
    modal.hidden = true;
    if (returnFocus && returnFocus.focus) returnFocus.focus();
  }
  function showToast(text) {
    toast.textContent = text;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.hidden = true; }, 3000);
  }

  $("#btn-feedback").addEventListener("click", openModal);
  $("#feedback-close").addEventListener("click", closeModal);
  $("#feedback-cancel").addEventListener("click", closeModal);
  modal.addEventListener("click", function (e) { if (e.target === modal) closeModal(); });
  message.addEventListener("input", updateCounter);
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    closeModal();
    form.reset();
    updateCounter();
    showToast("Dziękujemy, uwaga wysłana");
  });

  // ---------- Keyboard ----------
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (!modal.hidden) { closeModal(); return; }
    if (state.mode === "profile") setMode("watershed");
  });

  // ---------- Initial state ----------
  updateCounter();
  setMode("watershed");
})();
