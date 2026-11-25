// What a GUI's page does around the kit's base maps, for both test pages: the entries its
// server allows (`?allowed=` ids, every entry without it) and the deployment's own base maps
// (`?own=1`, own.json), the words of an English page (`?lang=en`), and what the tests read.

export const params = new URLSearchParams(location.search);

/** Words of an English page in place of BASEMAP_TEXTS, labels included. */
export const ENGLISH = {
  group: "Base maps",
  name: "Base map",
  none: "no base map",
  failed: "Base map not responding",
  credit: "Show or hide the base map's credit",
  labels: {
    openfreemap: "OpenFreeMap grey",
    "gugik-osm": "OSM GUGiK grey (Poland only)",
    "gugik-ortho": "GUGiK orthophoto",
  },
};

/** The page's own data: a square around Warsaw and a point in it. */
export const OVERLAY = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {},
      geometry: {
        type: "Polygon",
        coordinates: [[[20.6, 52.0], [21.4, 52.0], [21.4, 52.45], [20.6, 52.45], [20.6, 52.0]]],
      },
    },
    { type: "Feature", properties: {}, geometry: { type: "Point", coordinates: [21.01, 52.23] } },
  ],
};

/** The vendored glyphs, as a GUI passes them. */
export const GLYPHS = new URL("vendor/glyphs/{fontstack}/{range}.pbf", location.href).href
  .replace(/%7B/gi, "{")
  .replace(/%7D/gi, "}");

/** What the tests read: failures, rejections, faults of the page and CSP violations. */
export const test = (window.basemapTest = {
  failures: [],
  rejections: [],
  problems: [],
  cspViolations: [],
  ready: false,
});

document.addEventListener("securitypolicyviolation", (event) => {
  test.cspViolations.push(`${event.violatedDirective} ${event.blockedURI}`);
});

/** The entries the page receives, as from its server. */
export async function served() {
  const catalogue = await (await fetch("kit/nogat-basemaps.json")).json();
  const ids = params.has("allowed")
    ? params.get("allowed").split(",").filter(Boolean)
    : catalogue.entries.map((entry) => entry.id);
  const entries = catalogue.entries.filter((entry) => ids.includes(entry.id));
  if (params.get("own") !== "1") return entries;
  return [...entries, ...(await (await fetch("own.json")).json())];
}

/** The switcher with the entries, in the page's language. */
export function switcher(entries) {
  const element = document.querySelector("nogat-basemaps");
  if (params.get("lang") === "en") {
    document.documentElement.lang = "en";
    element.texts = ENGLISH;
  }
  element.entries = entries;
  return element;
}

/** Record a failure as the GUI does: the switcher marks the entry. */
export function failure(element) {
  return (id) => {
    test.failures.push(id);
    element.fail(id);
  };
}

/** Record a rejection other than a call overtaken by a later one. */
export function rejected(id, error) {
  if (error?.name !== "AbortError") test.rejections.push([id, String(error?.message ?? error)]);
}
