const MAX_RADIUS_M = 2000;
const API_BASE = "http://127.0.0.1:8000";

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
const resultsStatus = document.getElementById("results-status");
const resultsList = document.getElementById("results-list");

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

function clearResults() {
  resultsStatus.textContent = "";
  resultsList.innerHTML = "";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderResults(data) {
  const places = data.places || [];
  resultsStatus.textContent = places.length
    ? `${places.length} places along ${data.stops.length} stops`
    : "No places found along this route";

  resultsList.innerHTML = places
    .map(
      (place) => `
      <article class="result-item">
        <p class="result-station">${escapeHtml(place.station)}</p>
        <h3 class="result-name">${escapeHtml(place.name)}</h3>
        <p class="result-desc">${escapeHtml(place.description)}</p>
      </article>
    `
    )
    .join("");
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
  clearResults();
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
  clearResults();
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
  clearResults();
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
  clearResults();
  refreshMarkerStyles();
  updatePanel();
});

goBtn.addEventListener("click", async () => {
  if (!state.from || !state.to) return;

  goBtn.disabled = true;
  resultsStatus.textContent = "Searching along route…";
  resultsList.innerHTML = "";

  const url = new URL(`${API_BASE}/api/route`, window.location.origin);
  url.searchParams.set("from", state.from);
  url.searchParams.set("to", state.to);
  url.searchParams.set("kind", state.kind);
  url.searchParams.set("radius", String(state.radiusM));

  try {
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Request failed");
    }
    renderResults(data);
  } catch (err) {
    resultsStatus.textContent = err.message || "Could not reach backend";
  } finally {
    updatePanel();
  }
});

setRadius(state.radiusM);
updatePanel();

window.addEventListener("resize", () => {
  map.invalidateSize();
});

loadStations();
