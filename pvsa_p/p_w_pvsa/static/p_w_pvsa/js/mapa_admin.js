(function () {
  const STYLE = {
    version: 8,
    sources: {
      sat: {
        type: "raster",
        tiles: ["https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"],
        tileSize: 256,
        attribution: "Esri"
      }
    },
    layers: [{ id: "sat", type: "raster", source: "sat" }]
  };

  const el = document.getElementById("mapa-data");
  const fc = el ? JSON.parse(el.textContent) : { type: "FeatureCollection", features: [] };

  const map = new maplibregl.Map({
    container: "mapaAdmin",
    style: STYLE,
    center: [-71.484847, -32.752389],
    zoom: 15
  });
  map.addControl(new maplibregl.NavigationControl(), "top-right");

  const vistaSel = document.getElementById("mapVista");
  const sectorSel = document.getElementById("mapSector");
  const ubicSel = document.getElementById("mapUbicacion");
  const btnLimpiar = document.getElementById("btnLimpiar");
  const lista = document.getElementById("listaFeatures");

  function bboxOfFeatureCollection(fc) {
    let minX=999, minY=999, maxX=-999, maxY=-999;
    fc.features.forEach(f => {
      const coords = f.geometry?.coordinates?.[0] || [];
      coords.forEach(([x,y]) => {
        minX=Math.min(minX,x); minY=Math.min(minY,y);
        maxX=Math.max(maxX,x); maxY=Math.max(maxY,y);
      });
    });
    if (minX === 999) return null;
    return [[minX,minY],[maxX,maxY]];
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
      const badge = p.kind === "sector" ? "bg-success" : "bg-primary";

      const item = document.createElement("a");
      item.href = "javascript:void(0)";
      item.className = "list-group-item list-group-item-action";
      item.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <div class="fw-semibold">${p.name}</div>
            <div class="small text-muted">${kind} · ${p.sector_name}</div>
          </div>
          <span class="badge ${badge}">${kind}</span>
        </div>
      `;
      item.addEventListener("click", () => {
        zoomToFeature(f);
        popupForFeature(f);
      });
      lista.appendChild(item);
    });
  }

  function zoomToFeature(f) {
    const coords = f.geometry?.coordinates?.[0] || [];
    let minX=999, minY=999, maxX=-999, maxY=-999;
    coords.forEach(([x,y]) => { minX=Math.min(minX,x); minY=Math.min(minY,y); maxX=Math.max(maxX,x); maxY=Math.max(maxY,y); });
    if (minX < 999) map.fitBounds([[minX,minY],[maxX,maxY]], { padding: 60 });
  }

  let popup = null;
  function popupForFeature(f, lngLat) {
    const p = f.properties || {};
    const html = `
      <div style="min-width:220px">
        <div class="fw-semibold mb-1">${p.name}</div>
        <div class="small text-muted mb-2">${p.kind.toUpperCase()} · ${p.sector_name}</div>
        <div class="d-grid gap-1">
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

  function applyFilters() {
    const vista = vistaSel.value; // todo/sector/ubicacion
    const sectorId = sectorSel.value;
    const ubicId = ubicSel.value;

    // filtrar opciones de ubicacion por sector
    Array.from(ubicSel.options).forEach(opt => {
      const s = opt.getAttribute("data-sector");
      if (!s) return; // "Todas"
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
      if (ubicId && p.kind === "sector") return false; // si eliges ubicación, no muestres sectores
      return true;
    });

    const out = { type: "FeatureCollection", features: filtered };
    map.getSource("polys")?.setData(out);

    renderList(filtered);

    const bb = bboxOfFeatureCollection(out);
    if (bb) map.fitBounds(bb, { padding: 60 });
  }

  map.on("load", () => {
    map.addSource("polys", { type: "geojson", data: fc });

    map.addLayer({
      id: "fill",
      type: "fill",
      source: "polys",
      paint: {
        "fill-color": [
          "case",
          ["==", ["get", "kind"], "sector"], "#06b6b9",
          "#0d6efd"
        ],
        "fill-opacity": 0.25
      }
    });

    map.addLayer({
      id: "line",
      type: "line",
      source: "polys",
      paint: {
        "line-color": [
          "case",
          ["==", ["get", "kind"], "sector"], "#06b6b9",
          "#0d6efd"
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

    // inicial
    renderList(fc.features);
    const bb = bboxOfFeatureCollection(fc);
    if (bb) map.fitBounds(bb, { padding: 60 });

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