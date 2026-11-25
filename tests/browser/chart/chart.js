// A GUI's page around the kit's chart module: the charts the tests draw and what they read.
import * as kit from "./kit/nogat-chart.js";

const DAY = 86400000;
const dayOf = (year, month, day = 1) => Math.round(Date.UTC(year, month, day) / DAY);
const FIRST = dayOf(2020, 0);

/** What the tests read: the page's faults, CSP violations, the callbacks and the renders. */
const test = (window.chartTest = {
  kit,
  FIRST,
  problems: [],
  cspViolations: [],
  ranges: [],
  readouts: [],
  renders: 0,
  chart: null,
});

document.addEventListener("securitypolicyviolation", (event) => {
  test.cspViolations.push(`${event.violatedDirective} ${event.blockedURI}`);
});
window.addEventListener("error", (event) => test.problems.push(String(event.message)));
window.addEventListener("unhandledrejection", (event) => {
  test.problems.push(String(event.reason));
});

/** `count` points from `make(at)`, the index from 0. */
const range = (count, make) => Array.from({ length: count }, (_, at) => make(at));

/**
 * Daily discharge from 2020-01-01: a seasonal wave and a weekly ripple, ten days of March
 * missing and a flood of ten days in early July.
 */
function daily(days) {
  return range(days, (at) => {
    const flood = at >= 180 && at < 190 ? 400 : 0;
    const value = 100 + 50 * Math.sin((2 * Math.PI * at) / 365) + (at % 7) + flood;
    return [FIRST + at, at >= 60 && at < 70 ? null : value];
  });
}

/** A rating curve: measured flows and levels, and the fitted curve. */
function rating() {
  const flow = (level) => 0.002 * level ** 1.8;
  const fit = range(101, (at) => [flow(at * 5), at * 5]);
  const measured = range(40, (at) => {
    const level = 10 + at * 12;
    return [flow(level) * (1 + 0.05 * Math.sin(at)), level];
  });
  return { fit, measured };
}

/** A unit hydrograph's flow of 12 h in minutes, its peak of 45 m³/s at 200 min. */
const hydrograph = (at) => [at, 5 + 40 * Math.exp(-(((at - 200) / 90) ** 2))];
/** Ten-minute rain over two hours [mm]. */
const rain = (at) => [at * 10, 2 + (at % 4)];
/** An hourly water level from 2020-01-01 [cm]. */
const hourly = (at) => [FIRST + at / 24, 150 + 20 * Math.sin(at / 12)];

const SPECS = {
  daily: ({ days = 3000, zoom, fit = true, fixedY = false } = {}) => ({
    title: "Przepływ dobowy",
    x: { scale: "date" },
    y: {
      label: "Q [m³/s]",
      unit: "m³/s",
      zero: false,
      digits: 1,
      ...(fixedY ? { min: 0, max: 600 } : {}),
    },
    series: [{ id: "q", kind: "line", label: "Q", data: daily(days) }],
    readout: true,
    ...(zoom === undefined ? {} : { zoom }),
    ...(fit ? { fit: { ratio: 0.45, minHeight: 200 } } : {}),
    legend: true,
  }),
  months: () => ({
    title: "Przepływ w miesiącach",
    x: {
      scale: "linear",
      min: 1,
      max: 12,
      tickList: [{ value: 1, label: "I" }, { value: 12, label: "XII" }],
    },
    y: { label: "Q [m³/s]", unit: "m³/s" },
    series: [{ id: "m", kind: "line", data: range(12, (at) => [at + 1, 50 + at]) }],
    readout: true,
    zoom: false,
  }),
  rating: () => {
    const curve = rating();
    return {
      title: "Krzywa natężenia przepływu",
      x: { label: "Q [m³/s]", short: "Q" },
      y: { label: "H [cm]", short: "H", unit: "cm", digits: 0 },
      series: [
        { id: "measured", kind: "points", label: "Pomiary", data: curve.measured, cls: "s2" },
        { id: "fit", kind: "line", label: "Krzywa", data: curve.fit },
      ],
      readout: { series: "fit" },
      zoom: "xy",
      fit: { ratio: 0.6, minHeight: 220 },
      legend: true,
    };
  },
  scatter: () => ({
    title: "Punkty bez odczytu",
    x: { label: "x" },
    y: { label: "y" },
    series: [{ id: "p", kind: "points", data: rating().measured }],
    zoom: "xy",
    fit: { ratio: 0.6, minHeight: 220 },
  }),
  hydrograph: ({ readout = false } = {}) => ({
    title: "Hydrogram",
    x: { label: "czas [{unit}]", scale: "time" },
    y: { label: "Q [m³/s]", unit: "m³/s" },
    y2: { label: "P [mm]", unit: "mm" },
    series: [
      { id: "p", kind: "bars", axis: "y2", cls: "bar-p", data: range(12, rain) },
      { id: "q", kind: "line", data: range(721, hydrograph) },
    ],
    marks: [{ kind: "peak", x: 200, y: 45, label: "45 m³/s" }],
    readout,
    fit: { ratio: 0.5, minHeight: 220 },
  }),
  hourly: () => ({
    title: "Stan wody co godzinę",
    x: { scale: "datetime" },
    y: { label: "H [cm]", unit: "cm" },
    series: [{ id: "h", data: range(240, hourly) }],
    readout: true,
  }),
  duration: () => ({
    title: "Krzywa czasu trwania",
    x: { scale: "log", label: "czas trwania [%]" },
    y: { label: "Q [m³/s]" },
    series: [{ id: "c", data: range(99, (at) => [at + 1, 400 / (at + 2)]) }],
    readout: true,
  }),
  shares: () => ({
    title: "Pokrycie terenu",
    x: { label: "udział [%]" },
    y: { scale: "band" },
    series: [
      {
        id: "s",
        data: [{ x: 40, y: "Lasy" }, { x: 35, y: "Grunty orne" }, { x: 25, y: "Zabudowa" }],
      },
    ],
  }),
  probability: () => ({
    title: "Rozkład prawdopodobieństwa",
    x: { scale: "gumbel", domain: [99, 0.1] },
    y: { label: "WQ [m³/s]" },
    series: [{ id: "g", kind: "line", data: [[90, 10], [50, 25], [10, 40], [1, 50], [0.1, 70]] }],
    readout: true,
  }),
  extras: () => ({
    title: "Dwie zmienne",
    x: { scale: "date", tickLabels: false },
    y: { label: "H [cm]", unit: "cm", width: 64 },
    y2: { label: "Q [m³/s]", unit: "m³/s", side: "right", width: 64 },
    series: [
      { id: "h", kind: "line", label: "H", data: range(60, (at) => [FIRST + at, 200 + at]) },
      {
        id: "q",
        kind: "line",
        axis: "y2",
        label: "Q",
        data: range(60, (at) => [FIRST + at, 3 + at / 10]),
      },
      {
        id: "x",
        kind: "points",
        label: "Ekstrema",
        shape: "hollow",
        data: [
          { x: FIRST + 5, y: 205 },
          { x: FIRST + 20, y: 220, shape: "diamond" },
          { x: FIRST + 40, y: 240, shape: "dot" },
        ],
      },
    ],
    marks: [{ kind: "span", id: "gap", from: FIRST + 30, to: FIRST + 35 }],
    readout: true,
    fit: { ratio: 0.4, minHeight: 180 },
    legend: true,
  }),
};

/** Draw a chart of SPECS into #chart, the callbacks recorded and every render counted. */
test.draw = (name, options = {}) => {
  test.chart?.destroy();
  test.observer?.disconnect();
  test.ranges = [];
  test.readouts = [];
  test.renders = 0;
  const { texts, locale, dateFormat, ...rest } = options;
  const spec = {
    ...SPECS[name](rest),
    ...(texts ? { texts } : {}),
    ...(locale ? { locale } : {}),
    ...(dateFormat ? { dateFormat } : {}),
    onRange: (shown) => test.ranges.push(shown),
    onReadout: (index) => test.readouts.push(index),
  };
  test.spec = spec;
  test.chart = kit.drawChart(document.getElementById("chart"), spec);
  test.observer = new MutationObserver((records) => {
    const drawn = records.filter((record) => record.target === test.chart.svg);
    test.renders += drawn.some((record) => record.addedNodes.length) ? 1 : 0;
  });
  test.observer.observe(test.chart.svg, { childList: true });
  return true;
};

/** The same spec drawn again with new words, language or dates (a GUI's language switch). */
test.redraw = (options) => {
  test.spec = { ...test.spec, ...options };
  test.chart.update(test.spec);
};

/** The plot's frame in the viewBox, from its clip path. */
test.plot = () => {
  const rect = test.chart.svg.querySelector("clipPath rect");
  const [x, y, width, height] = ["x", "y", "width", "height"].map((name) =>
    Number(rect.getAttribute(name)),
  );
  return { left: x + 4, right: x + width - 4, top: y + 4, bottom: y + height - 4 };
};

/** A point of the viewBox on the screen, and back. */
test.toClient = (x, y) => {
  const point = new DOMPoint(x, y).matrixTransform(test.chart.svg.getScreenCTM());
  return [point.x, point.y];
};
test.toView = (x, y) => {
  const point = new DOMPoint(x, y).matrixTransform(test.chart.svg.getScreenCTM().inverse());
  return [point.x, point.y];
};

/** What a person sees: the range, the readout, the bar, the live region and the ticks. */
test.state = () => {
  const host = document.getElementById("chart");
  const line = host.querySelector(".readout-line");
  const bar = host.querySelector(".nogat-chart-zoom");
  const shown = (selector) => {
    const element = host.querySelector(selector);
    return Boolean(element) && !element.hidden && element.getClientRects().length > 0;
  };
  const ticks = (anchor) =>
    [...host.querySelectorAll("text.tick")]
      .filter((tick) => tick.getAttribute("text-anchor") === anchor)
      .map((tick) => tick.textContent);
  const reading = line && line.closest(".readout").getAttribute("visibility") !== "hidden";
  const rangeShown = shown(".nogat-chart-zoom-range");
  return {
    range: test.chart.zoom.range(),
    index: test.chart.readout.index(),
    readout: reading ? Number(line.getAttribute("x1")) : null,
    live: host.querySelector(".nogat-chart-sr").textContent,
    bar: bar.hidden
      ? null
      : {
          zoomIn: shown(".nogat-chart-zoom-in"),
          zoomOut: shown(".nogat-chart-zoom-out"),
          reset: shown(".nogat-chart-zoom-reset"),
          range: rangeShown ? host.querySelector(".nogat-chart-zoom-range").textContent : null,
        },
    xTicks: ticks("middle"),
    yTicks: ticks("end"),
    rightTicks: ticks("start"),
  };
};

/** Two animation frames: whatever a burst scheduled is drawn. */
test.frames = () =>
  new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));

test.ready = true;
