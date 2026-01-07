(function () {
  const container = document.getElementById("mapaEditor");
  if (!container) return;

  if (typeof maplibregl === "undefined") {
    console.error("MapLibre no cargó. Revisa el <script src> del CDN.");
    return;
  }

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

  const map = new maplibregl.Map({
    container: "mapaEditor",
    style: STYLE_SAT,
    center: [-71.484847, -32.752389],
    zoom: 18,
    maxZoom: MAX_ZOOM
  });

  map.addControl(new maplibregl.NavigationControl(), "top-right");

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
      if (!s) return;
      opt.hidden = sid ? s !== sid : false;
    });

    if (sid && ubicacionExistente.value) {
      const opt = ubicacionExistente.selectedOptions[0];
      if (opt && opt.hidden) ubicacionExistente.value = "";
    }
  }

  if (tipoRegistro) tipoRegistro.addEventListener("change", updateBloques);
  if (sectorParaUbicacion) sectorParaUbicacion.addEventListener("change", filterUbicacionesBySector);

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

  // cargar geom inicial si existe (modo editar)
  function loadInitialGeomIfAny() {
    const el = document.getElementById("geom-inicial");
    if (!el) return;

    try {
      const geom = JSON.parse(el.textContent);
      const ring = geom?.coordinates?.[0] || [];
      if (ring.length >= 4) {
        points = ring.slice(0, ring.length - 1);
        refreshDraw();

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

  map.on("load", () => {
    ensureDrawLayers();
    refreshDraw();
    setModeLabel();
    setCursor();
    updateBloques();
    filterUbicacionesBySector();
    loadInitialGeomIfAny();
  });

  map.on("click", (e) => {
    if (!marking) return;
    points.push([e.lngLat.lng, e.lngLat.lat]);
    refreshDraw();
  });

  if (btnMarcar) {
    btnMarcar.addEventListener("click", () => {
      marking = !marking;
      setModeLabel();
      setCursor();

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