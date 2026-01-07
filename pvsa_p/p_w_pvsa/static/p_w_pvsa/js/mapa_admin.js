(function () {
  const MAX_ZOOM = 19;

  const STYLE = {
    version: 8,
    sources: {
      sat: {
        type: "raster",
        tiles: ["https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"],
        tileSize: 256,
        maxzoom: MAX_ZOOM,
        attribution: "Esri"
      }
    },
    layers: [{ id: "sat", type: "raster", source: "sat" }]
  };

  const el = document.getElementById("mapa-data");
  const fc0 = el ? JSON.parse(el.textContent) : { type: "FeatureCollection", features: [] };

  // 🔥 Aseguramos IDs únicos para feature-state
  const fc = {
    type: "FeatureCollection",
    features: (fc0.features || []).map((f) => {
      const p = f.properties || {};
      const id =
        p.kind === "sector" ? `sector-${p.sector_id}` :
        p.kind === "ubicacion" ? `ubicacion-${p.id}` :
        `x-${Math.random().toString(16).slice(2)}`;

      return { ...f, id };
    })
  };

  const map = new maplibregl.Map({
    container: "mapaAdmin",
    style: STYLE,
    center: [-71.484847, -32.752389],
    zoom: 15,
    maxZoom: MAX_ZOOM
  });

  map.addControl(new maplibregl.NavigationControl(), "top-right");

  const vistaSel = document.getElementById("mapVista");
  const sectorSel = document.getElementById("mapSector");
  const ubicSel = document.getElementById("mapUbicacion");
  const btnLimpiar = document.getElementById("btnLimpiar");
  const lista = document.getElementById("listaFeatures");

  let popup = null;

  // stats cache (desde fetch)
  let statsSector = {};
  let statsUbic = {};

  // =========================
  // COLOR por % BUENO
  // =========================
  function clamp(n, a, b) { return Math.max(a, Math.min(b, n)); }

  function colorForPct(pct) {
    pct = Number(pct);
    if (!isFinite(pct)) return "#64748b";

    if (pct >= 65) {
      // 65 -> verde suave, 100 -> verde intenso
      const t = (clamp(pct, 65, 100) - 65) / 35;
      // interpolación simple entre dos verdes
      // 65: #86efac (claro) 100: #16a34a (intenso)
      return mixHex("#86efac", "#16a34a", t);
    }
    if (pct >= 50) {
      // 50..65 amarillo
      // puedes hacerlo fijo amarillo:
      return "#facc15";
    }
    // 0..49 rojo con intensidad
    const t = clamp(pct, 0, 49) / 49; // 0 -> 0, 49 -> 1
    // 0: #7f1d1d (rojo oscuro) 49: #f87171 (rojo suave)
    return mixHex("#7f1d1d", "#f87171", t);
  }

  function mixHex(a, b, t) {
    const pa = hexToRgb(a), pb = hexToRgb(b);
    const r = Math.round(pa.r + (pb.r - pa.r) * t);
    const g = Math.round(pa.g + (pb.g - pa.g) * t);
    const bl = Math.round(pa.b + (pb.b - pa.b) * t);
    return rgbToHex(r, g, bl);
  }

  function hexToRgb(h) {
    const x = h.replace("#", "").trim();
    const v = x.length === 3 ? x.split("").map(c => c + c).join("") : x;
    return {
      r: parseInt(v.slice(0, 2), 16),
      g: parseInt(v.slice(2, 4), 16),
      b: parseInt(v.slice(4, 6), 16),
    };
  }

  function rgbToHex(r, g, b) {
    const f = (n) => n.toString(16).padStart(2, "0");
    return `#${f(r)}${f(g)}${f(b)}`;
  }

  function badgeForPct(pct) {
    pct = Number(pct);
    if (!isFinite(pct)) return { label: "Sin datos", color: "#64748b" };
    return { label: `${pct}% Bueno`, color: colorForPct(pct) };
  }

  // =========================
  // BBOX + LIST
  // =========================
  function bboxOfFeatureCollection(fc) {
    let minX = 999, minY = 999, maxX = -999, maxY = -999;
    fc.features.forEach(f => {
      const coords = f.geometry?.coordinates?.[0] || [];
      coords.forEach(([x, y]) => {
        minX = Math.min(minX, x); minY = Math.min(minY, y);
        maxX = Math.max(maxX, x); maxY = Math.max(maxY, y);
      });
    });
    if (minX === 999) return null;
    return [[minX, minY], [maxX, maxY]];
  }

  function zoomToFeature(f) {
    const coords = f.geometry?.coordinates?.[0] || [];
    let minX = 999, minY = 999, maxX = -999, maxY = -999;
    coords.forEach(([x, y]) => {
      minX = Math.min(minX, x); minY = Math.min(minY, y);
      maxX = Math.max(maxX, x); maxY = Math.max(maxY, y);
    });
    if (minX < 999) map.fitBounds([[minX, minY], [maxX, maxY]], { padding: 60, maxZoom: MAX_ZOOM });
  }

  function getPctBuenasFromFeature(f) {
    const p = f.properties || {};
    if (p.kind === "sector") return statsSector[String(p.sector_id)]?.pct_buenas ?? null;
    if (p.kind === "ubicacion") return statsUbic[String(p.id)]?.pct_buenas ?? null;
    return null;
  }

  function popupForFeature(f, lngLat) {
    const p = f.properties || {};
    const pct = getPctBuenasFromFeature(f);
    const badge = badgeForPct(pct);

    const bar = (pct === null || pct === undefined)
      ? `<div class="small text-muted">Sin datos para calcular % Bueno</div>`
      : `
        <div class="mt-2">
          <div class="d-flex justify-content-between small">
            <span class="text-muted">Calidad</span>
            <span class="fw-semibold">${pct}% Bueno</span>
          </div>
          <div style="height:10px; background:#e5e7eb; border-radius:999px; overflow:hidden;">
            <div style="width:${Math.max(0, Math.min(100, pct))}%; height:10px; background:${badge.color};"></div>
          </div>
        </div>
      `;

    const html = `
      <div style="min-width:240px">
        <div class="d-flex justify-content-between align-items-start gap-2">
          <div>
            <div class="fw-semibold mb-1">${p.name || "-"}</div>
            <div class="small text-muted">${(p.kind || "").toUpperCase()} · ${p.sector_name || ""}</div>
          </div>
          <span style="
            font-size:12px;
            color:white;
            background:${badge.color};
            padding:4px 8px;
            border-radius:999px;
            white-space:nowrap;
          ">${badge.label}</span>
        </div>

        ${bar}

        <div class="d-grid gap-1 mt-3">
          <a class="btn btn-sm btn-outline-primary" href="${p.detail_url}">Detalles</a>
          <a class="btn btn-sm btn-primary" href="${p.edit_geom_url}">Editar polígono</a>
        </div>
      </div>
    `;

    if (popup) popup.remove();
    popup = new maplibregl.Popup({ closeOnClick: true })
      .setLngLat(lngLat || map.getCenter())
      .setHTML(html)
      .addTo(map);
  }

  function renderList(features) {
    lista.innerHTML = "";
    if (!features.length) {
      lista.innerHTML = `<div class="text-muted small">No hay polígonos guardados aún.</div>`;
      return;
    }

    features.forEach(f => {
      const p = f.properties || {};
      const kind = p.kind === "sector" ? "SECTOR" : "UBICACION";

      const pct = getPctBuenasFromFeature(f);
      const badge = badgeForPct(pct);

      const item = document.createElement("a");
      item.href = "javascript:void(0)";
      item.className = "list-group-item list-group-item-action";
      item.innerHTML = `
        <div class="d-flex justify-content-between align-items-center gap-2">
          <div>
            <div class="fw-semibold">${p.name || "-"}</div>
            <div class="small text-muted">${kind} · ${p.sector_name || ""}</div>
          </div>
          <span style="
            font-size:12px;
            color:white;
            background:${badge.color};
            padding:4px 8px;
            border-radius:999px;
          ">${badge.label}</span>
        </div>
      `;
      item.addEventListener("click", () => {
        zoomToFeature(f);
        popupForFeature(f);
      });
      lista.appendChild(item);
    });
  }

  // =========================
  // FILTROS
  // =========================
  function applyFilters() {
    const vista = vistaSel.value; // todo/sector/ubicacion
    const sectorId = sectorSel.value;
    const ubicId = ubicSel.value;

    // filtrar opciones de ubicacion por sector
    Array.from(ubicSel.options).forEach(opt => {
      const s = opt.getAttribute("data-sector");
      if (!s) return;
      opt.hidden = sectorId ? (s !== sectorId) : false;
    });
    if (sectorId && ubicSel.value) {
      const opt = ubicSel.selectedOptions[0];
      if (opt && opt.hidden) ubicSel.value = "";
    }

    const filtered = fc.features.filter(f => {
      const p = f.properties || {};
      if (vista !== "todo" && p.kind !== vista) return false;
      if (sectorId && String(p.sector_id) !== String(sectorId)) return false;
      if (ubicId && p.kind === "ubicacion" && String(p.id) !== String(ubicId)) return false;
      if (ubicId && p.kind === "sector") return false;
      return true;
    });

    const out = { type: "FeatureCollection", features: filtered };
    map.getSource("polys")?.setData(out);

    // recalcular feature-state visible (para pintar por %)
    setPctStates(filtered);

    renderList(filtered);

    const bb = bboxOfFeatureCollection(out);
    if (bb) map.fitBounds(bb, { padding: 60, maxZoom: MAX_ZOOM });
  }

  // =========================
  // FEATURE-STATE (pintar por %)
  // =========================
  function setPctStates(features) {
    // Limpiamos estados para todos (opcional, pero evita “arrastre”)
    (fc.features || []).forEach(f => {
      try { map.setFeatureState({ source: "polys", id: f.id }, { hasPct: false, pct: null }); } catch (e) {}
    });

    features.forEach(f => {
      const pct = getPctBuenasFromFeature(f);
      const has = pct !== null && pct !== undefined && isFinite(Number(pct));
      try {
        map.setFeatureState(
          { source: "polys", id: f.id },
          { hasPct: has, pct: has ? Number(pct) : null }
        );
      } catch (e) {}
    });
  }

  // =========================
  // FETCH STATS (MISMO VIEW)
  // =========================
  async function loadStats() {
    try {
      const res = await fetch(window.location.href, {
        headers: { "X-Requested-With": "XMLHttpRequest" }
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();

      statsSector = data.sector || {};
      statsUbic = data.ubicacion || {};
    } catch (e) {
      console.error("No se pudieron cargar stats del mapa:", e);
      statsSector = {};
      statsUbic = {};
    }
  }

  // =========================
  // MAP LOAD
  // =========================
  map.on("load", async () => {
    map.addSource("polys", { type: "geojson", data: fc });

    // Fill por % bueno con feature-state
    map.addLayer({
      id: "fill",
      type: "fill",
      source: "polys",
      paint: {
        "fill-color": [
          "case",
          ["==", ["feature-state", "hasPct"], true],
          [
            "case",
            [">=", ["feature-state", "pct"], 65],
            ["interpolate", ["linear"], ["feature-state", "pct"], 65, "#86efac", 100, "#16a34a"],
            [">=", ["feature-state", "pct"], 50],
            ["interpolate", ["linear"], ["feature-state", "pct"], 50, "#facc15", 65, "#facc15"],
            ["interpolate", ["linear"], ["feature-state", "pct"], 0, "#7f1d1d", 49, "#f87171"]
          ],
          // fallback si no hay pct
          ["case", ["==", ["get", "kind"], "sector"], "#06b6b9", "#0d6efd"]
        ],
        "fill-opacity": 0.28
      }
    });

    map.addLayer({
      id: "line",
      type: "line",
      source: "polys",
      paint: {
        "line-color": [
          "case",
          ["==", ["feature-state", "hasPct"], true],
          [
            "case",
            [">=", ["feature-state", "pct"], 65],
            "#15803d",
            [">=", ["feature-state", "pct"], 50],
            "#a16207",
            "#991b1b"
          ],
          "#0f172a"
        ],
        "line-width": 3
      }
    });

    map.addLayer({
      id: "labels",
      type: "symbol",
      source: "polys",
      layout: {
        "text-field": ["get", "name"],
        "text-size": 14
      }
    });

    map.on("click", "fill", (e) => {
      const f = e.features && e.features[0];
      if (!f) return;
      popupForFeature(f, e.lngLat);
    });

    // 1) cargar stats
    await loadStats();

    // 2) render inicial
    renderList(fc.features);

    // 3) set feature states iniciales
    setPctStates(fc.features);

    // 4) bounds inicial
    const bb = bboxOfFeatureCollection(fc);
    if (bb) map.fitBounds(bb, { padding: 60, maxZoom: MAX_ZOOM });

    // eventos filtros
    vistaSel.addEventListener("change", applyFilters);
    sectorSel.addEventListener("change", applyFilters);
    ubicSel.addEventListener("change", applyFilters);

    btnLimpiar.addEventListener("click", () => {
      vistaSel.value = "todo";
      sectorSel.value = "";
      ubicSel.value = "";
      applyFilters();
    });

    applyFilters();
  });
})();