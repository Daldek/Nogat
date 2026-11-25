// A GUI on Leaflet 1.9.4 with maplibre-gl-leaflet 0.0.22 over MapLibre GL JS 4.7.1
// (Hydrograf's): its own overlays, the kit's switcher and `leafletBasemap`'s layer under them.
import { leafletBasemap, repaintMaplibreBasemap } from "./kit/nogat-basemaps.js";
import { GLYPHS, OVERLAY, failure, params, rejected, served, switcher, test } from "./common.js";

const L = window.L;
const entries = await served();
const element = switcher(entries);
const map = L.map("the-map", { center: [52.2, 21.0], zoom: 7 });
L.geoJSON(OVERLAY, {
  style: { color: "#284b63", fillOpacity: 0.25 },
  pointToLayer: (feature, at) => L.circleMarker(at, { color: "#dc2626", radius: 6 }),
}).addTo(map);

const onFailure = failure(element);
let layer = null;
let wanted = null;

/** Draw the chosen base map, as a GUI does on the switcher's `change`. */
async function show(id) {
  test.shown = id;
  wanted = id;
  if (layer) map.removeLayer(layer);
  layer = null;
  const entry = entries.find((candidate) => candidate.id === id);
  if (!entry) return;
  const locale = params.get("lang") === "en" ? "en" : "pl";
  const options = { glyphs: GLYPHS, locale, onFailure, texts: element.texts };
  try {
    const made = await leafletBasemap(L, entry, options);
    if (wanted !== id) return;
    layer = made.addTo(map);
  } catch (error) {
    rejected(id, error);
  }
}

element.addEventListener("change", (event) => {
  test.pending = show(event.detail.id);
});
test.map = map;
test.switcher = element;
test.show = show;
test.layer = () => layer;
test.gl = () => layer?.getMaplibreMap?.() ?? null;
test.repaint = () => {
  const gl = test.gl();
  if (gl) repaintMaplibreBasemap(gl);
};
test.pending = show(element.value);
await test.pending;
test.ready = true;
