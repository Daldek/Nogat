// A GUI on MapLibre GL JS 6.14.0 (Obserwator's and Archiwista's): its own background and
// overlays, the kit's switcher and `maplibreBasemap` under the overlays.
import {
  maplibreBasemap,
  removeMaplibreBasemap,
  repaintMaplibreBasemap,
} from "./kit/nogat-basemaps.js";
import { GLYPHS, OVERLAY, failure, params, rejected, served, switcher, test } from "./common.js";

const maplibregl = await import("./vendor/maplibre-gl-6.14.0/maplibre-gl.mjs");

const entries = await served();
const element = switcher(entries);
const map = new maplibregl.Map({
  container: "the-map",
  style: {
    version: 8,
    glyphs: GLYPHS,
    sources: {},
    layers: [{ id: "background", type: "background", paint: { "background-color": "#c8d0da" } }],
  },
  center: [21.0, 52.2],
  zoom: 6,
  attributionControl: { compact: matchMedia("(max-width: 860px)").matches },
  locale: { "AttributionControl.ToggleAttribution": element.texts.credit },
});
map.on("error", (event) => {
  if (!event.sourceId) test.problems.push(String(event.error?.message ?? event.error));
});
await new Promise((resolve) => map.once("load", resolve));
map.addSource("overlay", { type: "geojson", data: OVERLAY });
map.addLayer({
  id: "overlay-fill",
  type: "fill",
  source: "overlay",
  filter: ["==", ["geometry-type"], "Polygon"],
  paint: { "fill-color": "#284b63", "fill-opacity": 0.25 },
});
map.addLayer({
  id: "overlay-point",
  type: "circle",
  source: "overlay",
  filter: ["==", ["geometry-type"], "Point"],
  paint: { "circle-color": "#dc2626", "circle-radius": 6 },
});

const onFailure = failure(element);

/** Draw the chosen base map, as a GUI does on the switcher's `change`. */
function show(id) {
  test.shown = id;
  const entry = entries.find((candidate) => candidate.id === id);
  if (!entry) {
    removeMaplibreBasemap(map);
    return Promise.resolve();
  }
  const locale = params.get("lang") === "en" ? "en" : "pl";
  return maplibreBasemap(entry, { map, glyphs: GLYPHS, locale, before: "overlay-fill", onFailure })
    .then(() => undefined, (error) => rejected(id, error));
}

element.addEventListener("change", (event) => {
  test.pending = show(event.detail.id);
});
test.map = map;
test.switcher = element;
test.show = show;
test.repaint = () => repaintMaplibreBasemap(map);
test.pending = show(element.value);
await test.pending;
test.ready = true;
