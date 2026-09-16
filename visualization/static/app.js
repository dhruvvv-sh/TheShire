const state = {
  plant: null,
  selectedUnitId: "pretreatment",
  feed: {},
  parameters: {},
  result: null,
};

const $ = (id) => document.getElementById(id);

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function formatWithUnit(value, unit, digits = 2) {
  const text = formatNumber(value, digits);
  return unit ? `${text} ${unit}` : text;
}

async function loadPlant() {
  const response = await fetch("/api/plant");
  if (!response.ok) {
    throw new Error("Could not load plant registry");
  }
  state.plant = await response.json();
  state.feed = { ...state.plant.feed.defaults };
  state.parameters = structuredClone(state.plant.default_parameters);
  $("plant-name").textContent = state.plant.name;
  renderFeedControls();
  renderUnitControls();
}

async function runSimulation() {
  const response = await fetch("/api/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      feed: state.feed,
      parameters: state.parameters,
    }),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Simulation failed");
  }
  state.result = await response.json();
  render();
}

function selectedUnit() {
  return state.plant.units.find((unit) => unit.id === state.selectedUnitId);
}

function renderFeedControls() {
  const host = $("feed-controls");
  host.innerHTML = "";
  state.plant.feed.parameters.forEach((param) => {
    host.appendChild(makeSlider(param, state.feed[param.id], (value) => {
      state.feed[param.id] = value;
      queueSimulate();
    }));
  });
}

function renderUnitControls() {
  const unit = selectedUnit();
  $("unit-params-title").textContent = `${unit.label} parameters`;
  $("unit-summary").textContent = unit.summary;
  const host = $("unit-controls");
  host.innerHTML = "";
  unit.parameters.forEach((param) => {
    host.appendChild(
      makeSlider(param, state.parameters[unit.id][param.id], (value) => {
        state.parameters[unit.id][param.id] = value;
        queueSimulate();
      })
    );
  });
}

function makeSlider(param, value, onChange) {
  const wrap = document.createElement("label");
  wrap.className = "control";
  const head = document.createElement("div");
  head.className = "control-head";
  const name = document.createElement("span");
  name.textContent = param.label;
  const readout = document.createElement("span");
  readout.className = "readout";
  const input = document.createElement("input");
  input.type = "range";
  input.min = param.min;
  input.max = param.max;
  input.step = param.step;
  input.value = value;
  const digits = String(param.step).includes(".") ? String(param.step).split(".")[1].length : 0;
  const updateReadout = () => {
    readout.textContent = formatWithUnit(Number(input.value), param.unit, digits);
  };
  updateReadout();
  input.addEventListener("input", () => {
    updateReadout();
    onChange(Number(input.value));
  });
  head.append(name, readout);
  wrap.append(head, input);
  return wrap;
}

function renderKpis() {
  const host = $("kpi-row");
  host.innerHTML = "";
  (state.result?.kpis || []).forEach((kpi) => {
    const el = document.createElement("div");
    el.className = "kpi";
    el.innerHTML = `<span class="label">${kpi.label}</span><span class="value">${formatNumber(kpi.value)}${kpi.unit ? `<span class="unit">${kpi.unit}</span>` : ""}</span>`;
    host.appendChild(el);
  });
}

function streamInto(unitId) {
  return state.result?.streams.find((stream) => stream.to === unitId);
}

function streamsOutOf(unitId) {
  return (state.result?.streams || []).filter((stream) => stream.from === unitId);
}

function renderMimic() {
  const host = $("mimic");
  host.innerHTML = "";
  const units = state.plant.units;

  units.forEach((unit, index) => {
    const incoming = streamInto(unit.id);
    const outlets = streamsOutOf(unit.id);
    const primaryOut = outlets.find((stream) => stream.to && units.some((item) => item.id === stream.to)) || outlets[0];
    const col = document.createElement("div");
    col.className = "node-col";
    col.innerHTML = `<div class="stream-chip">${incoming ? `${formatNumber(incoming.flow)} m³/h · ${formatNumber(incoming.pressure)} bar` : ""}</div>`;
    const button = document.createElement("button");
    button.type = "button";
    button.className = `unit-card${unit.id === state.selectedUnitId ? " selected" : ""}`;
    button.addEventListener("click", () => {
      state.selectedUnitId = unit.id;
      renderUnitControls();
      render();
    });
    button.innerHTML = `
      <div class="tag">${unit.short} · ${unit.status}</div>
      <h3>${unit.label}</h3>
      <div class="metric">${primaryOut ? `${formatNumber(primaryOut.pressure)} bar` : ""}</div>
    `;
    col.appendChild(button);
    host.appendChild(col);
    if (index < units.length - 1) {
      const pipe = document.createElement("div");
      pipe.className = "pipe";
      host.appendChild(pipe);
    }
  });

  const lastUnit = units[units.length - 1];
  const terminals = streamsOutOf(lastUnit?.id).filter(
    (stream) => !units.some((unit) => unit.id === stream.to)
  );
  if (terminals.length) {
    const branch = document.createElement("div");
    branch.className = "branch";
    terminals.forEach((stream) => {
      const kind = stream.id === "brine" ? "brine" : "product";
      branch.appendChild(terminus(stream.name, stream, kind));
    });
    host.appendChild(branch);
  }
}

function terminus(title, stream, kind) {
  const el = document.createElement("div");
  el.className = `terminus ${kind}`;
  el.innerHTML = `
    <div class="name">${title}</div>
    <div class="metric">${stream ? `${formatNumber(stream.flow)} m³/h` : ""}</div>
    <div class="metric">${stream ? `${formatNumber(stream.salinity)} mg/L` : ""}</div>
  `;
  return el;
}

function renderInternals() {
  const unit = selectedUnit();
  $("internals-title").textContent = `${unit.label} internals`;
  const host = $("internals");
  host.innerHTML = "";
  const details = state.result?.units?.[unit.id];
  const internals = details?.internals || [];
  internals.forEach((item) => {
    const schema = unit.internals.find((entry) => entry.id === item.id);
    const card = document.createElement("div");
    card.className = "internal-card";
    const metrics = (item.metrics || [])
      .map((metric) => `<span class="metric-pill">${metric.label}: ${formatWithUnit(metric.value, metric.unit)}</span>`)
      .join("");
    card.innerHTML = `
      <div>
        <h3>${item.label}</h3>
        <p>${schema?.detail || ""}</p>
      </div>
      <div class="metrics">${metrics}</div>
    `;
    host.appendChild(card);
  });
}

function renderTable() {
  const table = $("stream-table");
  const properties = state.plant.stream_properties;
  const streams = state.result?.streams || [];
  const head = `<tr><th>Stream</th>${properties.map((prop) => `<th>${prop.label}${prop.unit ? ` (${prop.unit})` : ""}</th>`).join("")}</tr>`;
  const body = streams
    .map((stream) => {
      const cells = properties
        .map((prop) => `<td>${formatNumber(stream[prop.id], prop.digits)}</td>`)
        .join("");
      return `<tr><td>${stream.name}</td>${cells}</tr>`;
    })
    .join("");
  table.innerHTML = head + body;
}

function render() {
  renderKpis();
  renderMimic();
  renderInternals();
  renderTable();
}

let timer = null;
function queueSimulate() {
  clearTimeout(timer);
  timer = setTimeout(() => {
    runSimulation().catch((error) => {
      document.querySelector(".app").innerHTML = `<p class="error">${error.message}</p>`;
    });
  }, 60);
}

loadPlant()
  .then(runSimulation)
  .catch((error) => {
    document.querySelector(".app").innerHTML = `<p class="error">${error.message}</p>`;
  });
