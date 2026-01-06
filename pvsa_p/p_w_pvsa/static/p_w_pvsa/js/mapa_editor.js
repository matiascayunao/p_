(function () {
  // Si no estamos en la página del editor, salimos sin romper nada
  const container = document.getElementById("mapaEditor");
  if (!container) return;

  // Si MapLibre no cargó, mostramos error claro y salimos
  if (typeof maplibregl === "undefined") {
    console.error("MapLibre no cargó. Revisa el <script src> del CDN.");
    return;
  }

  // ======================
  // STYLES (base maps)
  // ======================
  const MAX_ZOOM = 19;

  // Satelital (Esri)
  const STYLE_SAT = {
    version: 8,
    sources: {
      sat: {
        type: "raster",
        tiles: [
          "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ],
        tileSize: 256,
        maxzoom: MAX_ZOOM,
        attribution: "Esri"
      }
    },
    layers: [{ id: "sat", type: "raster", source: "sat" }]
  };

  // Mapa (CARTO Voyager)
  const STYLE_MAPA = {
    version: 8,
    sources: {
      carto: {
        type: "raster",
        tiles: [
          "https://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png",
          "https://b.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png",
          "https://c.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png",
          "https://d.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"
        ],
        tileSize: 256,
        maxzoom: MAX_ZOOM,
        attribution: "© OpenStreetMap contributors © CARTO"
      }
    },
    layers: [{ id: "carto", type: "raster", source: "carto" }]
  };

  // ======================
  // MAP INIT
  // ======================
  const map = new maplibregl.Map({
    container: "mapaEditor",
    style: STYLE_SAT,
    center: [-71.484847, -32.752389], // Puerto Ventanas / Valparaíso aprox
    zoom: 18,
    maxZoom: MAX_ZOOM
  });

  map.addControl(new maplibregl.NavigationControl(), "top-right");

  // ======================
  // UI ELEMENTS
  // ======================
  const btnMarcar = document.getElementById("btnMarcar");
  const btnDeshacer = document.getElementById("btnDeshacer");
  const btnLimpiar = document.getElementById("btnLimpiar");
  const btnListo = document.getElementById("btnListo");
  const estadoModo = document.getElementById("estadoModo");
  const contador = document.getElementById("contador");
  const geomInput = document.getElementById("geom_json");

  const modalEl = document.getElementById("modalGuardar");
  const modal = modalEl ? new bootstrap.Modal(modalEl) : null;

  const tipoRegistro = document.getElementById("tipoRegistro");
  const bloqueSector = document.getElementById("bloqueSector");
  const bloqueUbicacion = document.getElementById("bloqueUbicacion");
  const sectorParaUbicacion = document.getElementById("sectorParaUbicacion");
  const ubicacionExistente = document.getElementById("ubicacionExistente");

  function updateBloques() {
    if (!tipoRegistro || !bloqueSector || !bloqueUbicacion) return;
    const v = tipoRegistro.value;
    if (v === "sector") {
      bloqueSector.style.display = "";
      bloqueUbicacion.style.display = "none";
    } else {
      bloqueSector.style.display = "none";
      bloqueUbicacion.style.display = "";
    }
  }

  function filterUbicacionesBySector() {
    if (!sectorParaUbicacion || !ubicacionExistente) return;
    const sid = sectorParaUbicacion.value;

    Array.from(ubicacionExistente.options).forEach((opt) => {
      const s = opt.getAttribute("data-sector");
      if (!s) return; // "-- seleccionar --"
      opt.hidden = sid ? s !== sid : false;
    });

    if (sid && ubicacionExistente.value) {
      const opt = ubicacionExistente.selectedOptions[0];
      if (opt && opt.hidden) ubicacionExistente.value = "";
    }
  }

  if (tipoRegistro) tipoRegistro.addEventListener("change", updateBloques);
  if (sectorParaUbicacion) sectorParaUbicacion.addEventListener("change", filterUbicacionesBySector);

  // ======================
  // DIBUJO POR CLICK
  // ======================
  let points = [];
  let marking = false;

  function setCount() {
    if (contador) contador.textContent = `Puntos: ${points.length}`;
  }

  function setModeLabel() {
    if (!estadoModo) return;
    estadoModo.textContent = `Modo: ${marking ? "ON (click en el mapa)" : "OFF"}`;
  }

  function setCursor() {
    map.getCanvas().style.cursor = marking ? "crosshair" : "";
  }

  function geoPoints() {
    return {
      type: "FeatureCollection",
      features: points.map((p, i) => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: p },
        properties: { idx: i + 1 }
      }))
    };
  }

  function geoLineOrPoly() {
    if (points.length < 2) return { type: "FeatureCollection", features: [] };

    if (points.length < 3) {
      return {
        type: "FeatureCollection",
        features: [{
          type: "Feature",
          geometry: { type: "LineString", coordinates: points },
          properties: {}
        }]
      };
    }

    const ring = points.concat([points[0]]);
    return {
      type: "FeatureCollection",
      features: [{
        type: "Feature",
        geometry: { type: "Polygon", coordinates: [ring] },
        properties: {}
      }]
    };
  }

  function polygonGeometry() {
    if (points.length < 3) return null;
    const ring = points.concat([points[0]]);
    return { type: "Polygon", coordinates: [ring] };
  }

  function refreshDraw() {
    setCount();
    const srcPts = map.getSource("pts");
    const srcShape = map.getSource("shape");
    if (srcPts) srcPts.setData(geoPoints());
    if (srcShape) srcShape.setData(geoLineOrPoly());
  }

  function clearAll() {
    points = [];
    refreshDraw();
  }

  function undo() {
    points.pop();
    refreshDraw();
  }

  // cargar geom inicial si existe (modo editar)
  function loadInitialGeomIfAny() {
    const el = document.getElementById("geom-inicial");
    if (!el) return;

    try {
      const geom = JSON.parse(el.textContent);
      const ring = geom?.coordinates?.[0] || [];
      if (ring.length >= 4) {
        points = ring.slice(0, ring.length - 1); // quitamos el cierre
        refreshDraw();

        // zoom a bounds
        let minX = 999, minY = 999, maxX = -999, maxY = -999;
        ring.forEach(([x, y]) => {
          minX = Math.min(minX, x);
          minY = Math.min(minY, y);
          maxX = Math.max(maxX, x);
          maxY = Math.max(maxY, y);
        });
        if (minX < 999) map.fitBounds([[minX, minY], [maxX, maxY]], { padding: 60, maxZoom: MAX_ZOOM });
      }
    } catch (e) {}
  }

  // ======================
  // DB OVERLAY (opcional)
  // ======================
  function readDbGeojson() {
    const el = document.getElementById("mapa-data");
    if (!el) return null;
    try {
      const fc = JSON.parse(el.textContent);
      if (!fc || !fc.features) return null;
      return fc;
    } catch (e) {
      return null;
    }
  }

  const dbGeo = readDbGeojson();

  function ensureDbLayers() {
    if (!dbGeo) return;

    if (!map.getSource("db")) {
      map.addSource("db", { type: "geojson", data: dbGeo });
    } else {
      map.getSource("db").setData(dbGeo);
    }

    // fill
    if (!map.getLayer("db-fill")) {
      map.addLayer({
        id: "db-fill",
        type: "fill",
        source: "db",
        paint: {
          "fill-color": [
            "match",
            ["get", "kind"],
            "sector", "#2563eb",
            "ubicacion", "#16a34a",
            "#64748b"
          ],
          "fill-opacity": 0.18
        }
      });
    }

    // line
    if (!map.getLayer("db-line")) {
      map.addLayer({
        id: "db-line",
        type: "line",
        source: "db",
        paint: {
          "line-color": [
            "match",
            ["get", "kind"],
            "sector", "#1d4ed8",
            "ubicacion", "#15803d",
            "#475569"
          ],
          "line-width": 2
        }
      });
    }
  }

  function setOverlayMode(mode) {
    // mode: none | sector | ubicacion | all
    const hasFill = map.getLayer("db-fill");
    const hasLine = map.getLayer("db-line");
    if (!hasFill || !hasLine) return;

    if (mode === "none") {
      map.setLayoutProperty("db-fill", "visibility", "none");
      map.setLayoutProperty("db-line", "visibility", "none");
      return;
    }

    map.setLayoutProperty("db-fill", "visibility", "visible");
    map.setLayoutProperty("db-line", "visibility", "visible");

    const f =
      mode === "all" ? null :
      mode === "sector" ? ["==", ["get", "kind"], "sector"] :
      ["==", ["get", "kind"], "ubicacion"];

    // Para cambiar filtro, usamos setFilter
    map.setFilter("db-fill", f);
    map.setFilter("db-line", f);
  }

  // ======================
  // DIBUJO LAYERS
  // ======================
  function ensureDrawLayers() {
    if (!map.getSource("pts")) {
      map.addSource("pts", { type: "geojson", data: geoPoints() });
    }
    if (!map.getSource("shape")) {
      map.addSource("shape", { type: "geojson", data: geoLineOrPoly() });
    }

    if (!map.getLayer("shape-fill")) {
      map.addLayer({
        id: "shape-fill",
        type: "fill",
        source: "shape",
        paint: { "fill-color": "#06b6b9", "fill-opacity": 0.25 }
      });
    }
    if (!map.getLayer("shape-line")) {
      map.addLayer({
        id: "shape-line",
        type: "line",
        source: "shape",
        paint: { "line-color": "#06b6b9", "line-width": 3 }
      });
    }
    if (!map.getLayer("pts-layer")) {
      map.addLayer({
        id: "pts-layer",
        type: "circle",
        source: "pts",
        paint: { "circle-radius": 6, "circle-color": "#ef4444" }
      });
    }
    if (!map.getLayer("pts-label")) {
      map.addLayer({
        id: "pts-label",
        type: "symbol",
        source: "pts",
        layout: { "text-field": ["get", "idx"], "text-size": 12, "text-offset": [0, -1.2] }
      });
    }
  }

  // ======================
  // CONTROL PANEL (dentro del mapa)
  // ======================
  class PanelControl {
    onAdd(map) {
      this._map = map;
      const el = document.createElement("div");
      el.className = "maplibregl-ctrl maplibregl-ctrl-group";
      el.style.background = "transparent";
      el.style.boxShadow = "none";
      el.style.border = "0";

      const panel = document.createElement("div");
      panel.className = "map-panel";

      panel.innerHTML = `
        <div class="rowx">
          <label>Base</label>
          <select id="baseStyleSel">
            <option value="sat">Satélite</option>
            <option value="mapa">Mapa</option>
          </select>
        </div>
        <div class="rowx">
          <label>Overlay</label>
          <select id="overlaySel">
            <option value="none">Nada</option>
            <option value="sector">Sectores</option>
            <option value="ubicacion">Ubicaciones</option>
            <option value="all" selected>Todo</option>
          </select>
        </div>
        <div class="hint">Tip: activa “marcado” y haz click para agregar puntos.</div>
      `;

      el.appendChild(panel);

      const baseSel = panel.querySelector("#baseStyleSel");
      const overlaySel = panel.querySelector("#overlaySel");

      baseSel.addEventListener("change", () => {
        const v = baseSel.value;
        // setStyle borra layers/sources => luego reponemos en style.load
        map.setStyle(v === "sat" ? STYLE_SAT : STYLE_MAPA);
      });

      overlaySel.addEventListener("change", () => {
        setOverlayMode(overlaySel.value);
      });

      this._panel = panel;
      this._overlaySel = overlaySel;

      return el;
    }

    onRemove() {
      if (this._panel && this._panel.parentNode) this._panel.parentNode.remove();
      this._map = undefined;
    }
  }

  map.addControl(new PanelControl(), "top-left");

  // ======================
  // EVENTS
  // ======================
  function ensureAll() {
    ensureDrawLayers();
    ensureDbLayers();
    refreshDraw();
    setModeLabel();
    setCursor();
    updateBloques();
    filterUbicacionesBySector();

    // overlay default: todo (si existe db)
    setOverlayMode("all");
  }

  map.on("load", () => {
    ensureAll();
    loadInitialGeomIfAny();
  });

  // cada vez que cambias base (setStyle), hay que reponer layers/sources
  map.on("style.load", () => {
    ensureAll();
  });

  // Click en mapa para agregar punto (si modo ON)
  map.on("click", (e) => {
    if (!marking) return;
    points.push([e.lngLat.lng, e.lngLat.lat]);
    refreshDraw();
  });

  // ======================
  // BUTTONS
  // ======================
  if (btnMarcar) {
    btnMarcar.addEventListener("click", () => {
      marking = !marking;
      setModeLabel();
      setCursor();

      // feedback visual
      btnMarcar.classList.toggle("btn-outline-primary", !marking);
      btnMarcar.classList.toggle("btn-primary", marking);
      btnMarcar.textContent = marking ? "MARCADO ON (CLICK EN MAPA)" : "ACTIVAR MARCADO (CLICK)";
    });
  }

  if (btnDeshacer) btnDeshacer.addEventListener("click", undo);
  if (btnLimpiar) btnLimpiar.addEventListener("click", clearAll);

  if (btnListo) {
    btnListo.addEventListener("click", () => {
      const geom = polygonGeometry();
      if (!geom) return;

      if (geomInput) geomInput.value = JSON.stringify(geom);
      if (modal) modal.show();
    });
  }
})();