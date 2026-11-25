// What a GUI's page does around the kit's command builder: the catalog entry of one command
// (`?catalog=`, a key of catalogs.json), the GUI's bindings of the tool's format_command and
// parse_command (`?format=1`, `?parse=1`), the paths the app owns (`?paths=hidden`) and the
// options it supplies itself (`?hide=a,b`); and what the tests read.

const params = new URLSearchParams(location.search);

/** What the tests read and set. */
export const test = (window.formTest = {
  ready: false,
  changes: [],
  pastes: [],
  formatted: [],
  parsed: [],
  rejections: [],
  cspViolations: [],
  escaped: 0,
  // `{option, value, ms}`: format answers that call this many ms late.
  slow: null,
  // Whether the page takes a pasted line of another command (switching the form to it).
  switches: false,
});

document.addEventListener("securitypolicyviolation", (event) => {
  test.cspViolations.push(`${event.violatedDirective} ${event.blockedURI}`);
});
window.addEventListener("unhandledrejection", (event) => {
  test.rejections.push(String(event.reason?.message ?? event.reason));
});

const catalogs = await (await fetch("catalogs.json")).json();
const doc = catalogs[params.get("catalog") ?? "kartograf"];
const entries = Object.values(catalogs)
  .filter((item) => Array.isArray(item?.commands))
  .map((item) => ({ tool: item.tool, ...item.commands[0] }));

/** The tool's flag of an option, kebab case (AGI-3.1). */
const flag = (name) => `--${name.replace(/_/g, "-")}`;

/** A value as the made-up line writes it: lists joined by commas, objects as JSON. */
function written(value) {
  if (Array.isArray(value)) return value.join(",");
  if (value && typeof value === "object") return `'${JSON.stringify(value)}'`;
  return String(value);
}

/** The GUI's binding of format_command: the tool's server would answer it. */
async function formatLine(command, options) {
  test.formatted.push({ command, options });
  const slow = test.slow;
  if (slow && options[slow.option] === slow.value) {
    await new Promise((done) => setTimeout(done, slow.ms));
  }
  if (options.sheet === "X-0") {
    throw {
      schema: `${doc.tool}-error/1`,
      code: "validation_error",
      title: "Invalid input",
      message: "unknown sheet code X-0",
      details: { option: "sheet", reason: "unknown_sheet" },
    };
  }
  if (options.workers === 99) {
    throw { code: "source_unavailable", message: "the server does not answer", details: {} };
  }
  const words = [doc.tool, command];
  for (const [name, value] of Object.entries(options)) {
    if (value === true) words.push(flag(name));
    else if (value !== false) words.push(flag(name), written(value));
  }
  return words.join(" ");
}

/** The GUI's binding of parse_command: its server would answer it. */
async function parseLine(line) {
  test.parsed.push(line);
  const words = line.trim().split(/\s+/);
  if (words[0] !== doc.tool) {
    throw {
      code: "validation_error",
      message: `not a ${doc.tool} line`,
      details: { reason: "unknown_tool" },
    };
  }
  const command = `${words[1]} ${words[2]}`;
  const entry = entries.find((item) => item.tool === doc.tool && item.name === command);
  const options = {};
  for (let at = 3; at < words.length; at += 1) {
    const name = words[at].replace(/^--/, "").replace(/-/g, "_");
    const option = entry?.options.find((item) => item.name === name);
    if (!option) {
      throw {
        code: "validation_error",
        message: `unknown option ${words[at]}`,
        details: { option: name, reason: "unknown_option" },
      };
    }
    if (option.type === "boolean") {
      options[name] = true;
      continue;
    }
    const text = words[(at += 1)];
    if (option.type === "array") {
      const items = text.split(",");
      options[name] = option.items === "number" ? items.map(Number) : items;
    } else if (option.type === "integer" || option.type === "number") {
      options[name] = Number(text);
    } else if (option.type === "object") {
      options[name] = JSON.parse(text);
    } else {
      options[name] = text;
    }
  }
  return { command, options };
}

await customElements.whenDefined("nogat-command-form");
const form = document.querySelector("nogat-command-form");
if (params.has("paths")) form.setAttribute("paths", params.get("paths"));
if (params.has("hide")) form.hide = params.get("hide").split(",");
form.command = doc;
if (params.get("format") === "1") form.format = formatLine;
if (params.get("parse") === "1") form.parse = parseLine;
form.addEventListener("change", (event) => {
  if (event.target === form) test.changes.push(event.detail);
  else test.escaped += 1;
});
form.addEventListener("input", () => {
  test.escaped += 1;
});
form.addEventListener("nogat-command-paste", (event) => {
  test.pastes.push(event.detail);
  const named = event.detail.command;
  const other = entries.find((item) => item.tool === doc.tool && item.name === named);
  if (!test.switches || !other || event.detail.command === form.command.name) return;
  event.preventDefault();
  form.command = other;
  form.options = event.detail.options;
});
test.form = form;
test.catalogs = catalogs;
test.ready = true;
