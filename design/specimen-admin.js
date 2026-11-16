// Specimen of the kit's admin panel (specimen-admin.html, DEV-15.13): a fake admin API inside
// the page, so the panel runs from any static server (`python -m http.server` in design/).
// It answers the core routes of DEV-15.13 below api/admin/ from memory with the key "nogat",
// and the route "resources" of the specimen's own section „Zasoby”. Not a kit file: no GUI
// copies it. It loads before the kit's module, and the panel sends its first request only
// once both have run.

const KEY = "nogat";
const DAY = 86400000;
const now = Date.now();

try {
  const theme = localStorage.getItem("nogat-theme"); // the choice of specimen.html
  if (theme === "light" || theme === "dark") document.documentElement.dataset.theme = theme;
} catch {
  // storage blocked: the system theme
}

const MESSAGES = [
  "Po wybraniu stacji wykres się nie odświeża.",
  "Brakuje opisu jednostek na osi przepływu.",
  "Czy można dodać eksport do CSV z tabeli przepływów?",
  "Mapa ładuje się bardzo wolno na telefonie.",
  "Literówka w instrukcji: „hydrogrm”.",
  "Nie działa przycisk „Kopiuj do Hydrologa”.",
  "Prośba o ciemny motyw w oknie wydruku.",
];

const reports = Array.from({ length: 64 }, (_, i) => {
  const id = i + 1;
  return {
    id,
    created_at: new Date(now - (64 - id) * 5 * 3600000).toISOString(),
    message: MESSAGES[id % MESSAGES.length],
    context: {
      view: ["mapa", "stacja", "obliczenia"][id % 3],
      station: id % 2 ? null : `1520${String(id).padStart(5, "0")}`,
      parameters: { okres: "1h", prawdopodobienstwo: id % 5 ? 1 : 10 },
      app_version: "1.4.0",
    },
    is_read: id % 4 !== 0,
  };
});

const days = Array.from({ length: 120 }, (_, i) => {
  const visitors = 20 + ((i * 7) % 23);
  return {
    date: new Date(now - (119 - i) * DAY).toISOString().slice(0, 10),
    visitors,
    page_views: visitors * 3 + (i % 5),
    stations_opened: (i * 3) % 11,
    analyses_run: (i * 5) % 9,
    downloads: i % 4,
  };
});

const status = {
  app: "Hydrolog",
  version: "1.4.0",
  started_at: new Date(now - 3 * DAY - 4 * 3600000).toISOString(),
  uptime_s: 3 * 86400 + 4 * 3600,
  data_dir: "/srv/nogat/hydrolog",
  disk: { free_bytes: 182_400_000_000, total_bytes: 500_000_000_000 },
  checks: [
    { name: "data_dir", status: "ok", detail: "Katalog danych jest zapisywalny." },
    { name: "feedback_db", status: "warning", detail: "64 zgłoszenia czekają na obsłużenie." },
    { name: "hydrolog_command", status: "failed", detail: "Polecenie hydrolog nie odpowiada." },
  ],
};

function answer(code, body) {
  const type = code < 400 ? "application/json" : "application/problem+json";
  return new Response(JSON.stringify(body), {
    status: code,
    headers: { "Content-Type": type, "Cache-Control": "no-store" },
  });
}

function problem(code, httpStatus, reason) {
  const details = reason ? { reason } : {};
  return answer(httpStatus, { title: code, status: httpStatus, code, details });
}

function refusal(headers) {
  const key = headers.get("X-Admin-Key");
  if (!key) return "admin_key_missing";
  return key === KEY ? null : "admin_key_invalid";
}

function feedback(url) {
  const limit = Number(url.searchParams.get("limit") ?? 50);
  const offset = Number(url.searchParams.get("offset") ?? 0);
  if (!(limit >= 1 && limit <= 200) || !(offset >= 0)) return problem("validation_error", 400);
  const items = [...reports].reverse();
  const page = items.slice(offset, offset + limit);
  const unread = items.filter((item) => !item.is_read).length;
  return answer(200, { items: page, total: items.length, unread_count: unread });
}

function report(method, id, body) {
  const at = reports.findIndex((item) => String(item.id) === id);
  if (at < 0) return problem("not_found", 404);
  if (method === "DELETE") {
    reports.splice(at, 1);
    return answer(200, { status: "deleted" });
  }
  if (typeof body?.is_read !== "boolean") return problem("validation_error", 400);
  reports[at] = { ...reports[at], is_read: body.is_read };
  return answer(200, reports[at]);
}

function stats(url) {
  const to = url.searchParams.get("to") ?? days[days.length - 1].date;
  const from = url.searchParams.get("from") ?? days[Math.max(0, days.length - 30)].date;
  const shown = days.filter((day) => day.date >= from && day.date <= to);
  const totals = {};
  for (const key of ["page_views", "stations_opened", "analyses_run", "downloads"]) {
    totals[key] = shown.reduce((sum, day) => sum + day[key], 0);
  }
  return answer(200, { days: shown, totals });
}

const realFetch = window.fetch.bind(window);

window.fetch = async (input, init = {}) => {
  const url = new URL(input instanceof Request ? input.url : String(input), location.href);
  const at = url.pathname.indexOf("/api/admin/");
  if (url.origin !== location.origin || at < 0) return realFetch(input, init);
  const method = (init.method ?? "GET").toUpperCase();
  const reason = refusal(new Headers(init.headers ?? {}));
  if (reason) return problem("unauthorized", 401, reason);
  const route = url.pathname.slice(at + "/api/admin/".length);
  const body = typeof init.body === "string" ? JSON.parse(init.body) : null;
  if (method === "GET" && route === "feedback") return feedback(url);
  if (route.startsWith("feedback/") && (method === "PATCH" || method === "DELETE")) {
    return report(method, decodeURIComponent(route.slice("feedback/".length)), body);
  }
  if (method === "GET" && route === "stats") return stats(url);
  if (method === "GET" && route === "status") {
    const uptime = status.uptime_s + Math.floor((Date.now() - now) / 1000);
    return answer(200, { ...status, uptime_s: uptime });
  }
  if (method === "GET" && route === "resources") {
    const items = ["NMT 5 m: 205 arkuszy", "Graf zlewni: 870 odcinków", "Opady PMAXTP"];
    return answer(200, { items });
  }
  return problem("not_found", 404);
};

// The specimen's own section: it asks its route through the shell's adminFetch when shown.
const admin = document.querySelector("nogat-admin");
admin.addEventListener("nogat-admin-section", async (event) => {
  if (event.detail.id !== "resources") return;
  const list = document.getElementById("specimen-resources");
  const response = await admin.adminFetch("resources");
  if (!response.ok) return;
  const { items } = await response.json();
  list.replaceChildren(
    ...items.map((text) => {
      const item = document.createElement("li");
      item.textContent = text;
      return item;
    }),
  );
});
