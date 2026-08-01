const MAX_RADIUS_M = 2000;

const state = {
  from: null,
  to: null,
  kind: "shops",
  radiusM: 1000,
  stations: [],
  markers: new Map(),
};

const fromEl = document.getElementById("from-name");
const toEl = document.getElementById("to-name");
const fromSelect = document.getElementById("from-select");
const toSelect = document.getElementById("to-select");
const goBtn = document.getElementById("go-btn");
const clearBtn = document.getElementById("clear-btn");
const radiusInput = document.getElementById("radius-input");
const radiusValueEl = document.getElementById("radius-value");

function formatRadius(meters) {
  const km = meters / 1000;
  return `${km.toFixed(1)} km`;
}

function setRadius(meters) {
  const clamped = Math.min(MAX_RADIUS_M, Math.max(200, Math.round(Number(meters) || 1000)));
  state.radiusM = clamped;
  radiusInput.value = String(clamped);
  radiusValueEl.textContent = formatRadius(clamped);
  const pct = ((clamped - 200) / (MAX_RADIUS_M - 200)) * 100;
  radiusInput.style.setProperty("--radius-pct", `${pct}%`);
}

// Official LTA system map pixel size
const MAP_SIZE = 3600;
const imageBounds = [
  [0, 0],
  [MAP_SIZE, MAP_SIZE],
];

const map = L.map("map", {
  crs: L.CRS.Simple,
  minZoom: -3,
  maxZoom: 2,
  zoomSnap: 0.25,
  zoomDelta: 0.5,
  zoomControl: true,
  attributionControl: true,
});

L.imageOverlay("mrt-map.png", imageBounds, {
  attribution:
    '<a href="https://www.lta.gov.sg/content/ltagov/en/getting_around/public_transport/rail_network.html">LTA Rail System Map</a>',
}).addTo(map);

map.fitBounds(imageBounds, { padding: [12, 12] });
map.setMaxBounds(imageBounds);

function markerIcon(kind) {
  const cls =
    kind === "start"
      ? "station-marker selected-start"
      : kind === "end"
        ? "station-marker selected-end"
        : "station-marker";
  return L.divIcon({
    className: "",
    html: `<div class="${cls}"></div>`,
    iconSize: kind ? [18, 18] : [11, 11],
    iconAnchor: kind ? [9, 9] : [5.5, 5.5],
  });
}

function refreshMarkerStyles() {
  for (const [name, marker] of state.markers) {
    if (state.from === name) marker.setIcon(markerIcon("start"));
    else if (state.to === name) marker.setIcon(markerIcon("end"));
    else marker.setIcon(markerIcon(null));
  }
}

function updatePanel() {
  fromEl.textContent = state.from ?? "Tap a station";
  toEl.textContent = state.to ?? "Tap a station";
  fromEl.dataset.empty = state.from ? "false" : "true";
  toEl.dataset.empty = state.to ? "false" : "true";
  fromSelect.value = state.from ?? "";
  toSelect.value = state.to ?? "";
  goBtn.disabled = !(state.from && state.to && state.from !== state.to);
}

function selectStation(name) {
  if (!state.from || (state.from && state.to)) {
    state.from = name;
    state.to = null;
  } else if (name === state.from) {
    return;
  } else {
    state.to = name;
  }
  refreshMarkerStyles();
  updatePanel();

  const marker = state.markers.get(name);
  if (marker) map.panTo(marker.getLatLng());
}

function fillSelects(allNames) {
  const options = allNames
    .slice()
    .sort((a, b) => a.localeCompare(b))
    .map((name) => `<option value="${name}">${name}</option>`)
    .join("");
  fromSelect.innerHTML = `<option value="">Select start station</option>${options}`;
  toSelect.innerHTML = `<option value="">Select end station</option>${options}`;
}

async function loadStations() {
  const [positions, allStations] = await Promise.all([
    fetch("station-positions.json").then((r) => r.json()),
    fetch("stations.json").then((r) => r.json()),
  ]);

  state.stations = positions;
  fillSelects(allStations.map((s) => s.name));

  for (const station of positions) {
    // CRS.Simple uses [y, x]; y already flipped for this image
    const marker = L.marker([station.y, station.x], {
      icon: markerIcon(null),
      title: station.name,
    })
      .addTo(map)
      .bindTooltip(station.name, {
        direction: "top",
        offset: [0, -8],
        className: "station-tip",
        opacity: 0.95,
      });

    marker.on("click", () => selectStation(station.name));
    state.markers.set(station.name, marker);
  }

  setTimeout(() => {
    map.invalidateSize();
    map.fitBounds(imageBounds, { padding: [12, 12] });
  }, 50);
}

fromSelect.addEventListener("change", () => {
  if (!fromSelect.value) return;
  state.from = fromSelect.value;
  state.to = null;
  refreshMarkerStyles();
  updatePanel();
  const marker = state.markers.get(state.from);
  if (marker) map.panTo(marker.getLatLng());
});

toSelect.addEventListener("change", () => {
  if (!toSelect.value) return;
  if (!state.from || toSelect.value === state.from) {
    toSelect.value = "";
    return;
  }
  state.to = toSelect.value;
  refreshMarkerStyles();
  updatePanel();
  const marker = state.markers.get(state.to);
  if (marker) map.panTo(marker.getLatLng());
});

document.querySelectorAll(".kind").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".kind").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.kind = btn.dataset.kind;
  });
});

radiusInput.addEventListener("input", () => {
  setRadius(radiusInput.value);
});

clearBtn.addEventListener("click", () => {
  state.from = null;
  state.to = null;
  refreshMarkerStyles();
  updatePanel();
});

goBtn.addEventListener("click", () => {
  if (!state.from || !state.to) return;
  // Backend not connected yet
});

setRadius(state.radiusM);
updatePanel();

window.addEventListener("resize", () => {
  map.invalidateSize();
});

loadStations();
