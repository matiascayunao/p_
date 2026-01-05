(() => {
  const el = document.getElementById("map");
  if (!el) return;

  const CENTER = [-71.484847, -32.752389];

  const map = new maplibregl.Map({
    container: "map",
    style: "https://tiles.openfreemap.org/styles/bright",
    center: CENTER,
    zoom: 16.8,
    pitch: 60,
    bearing: -20,
    antialias: true,
  });

  map.addControl(new maplibregl.NavigationControl(), "top-right");

  // Si hay errores de capas/sources, te los muestra en consola
  map.on("error", (e) => {
    console.log("MAP ERROR:", e?.error || e);
  });

  map.on("load", () => {
    // 1) Encuentra una capa de labels para insertar debajo
    const layers = map.getStyle().layers || [];
    let labelLayerId;
    for (const l of layers) {
      if (l.type === "symbol" && l.layout && l.layout["text-field"]) {
        labelLayerId = l.id;
        break;
      }
    }

    // 2) Detecta el source correcto del estilo (esto es CLAVE)
    const sources = map.getStyle().sources || {};
    const sourceName =
      sources.openmaptiles ? "openmaptiles" :
      sources.openfreemap ? "openfreemap" :
      Object.keys(sources)[0]; // último recurso

    console.log("SOURCES:", Object.keys(sources));
    console.log("USING SOURCE:", sourceName);

    // 3) Agrega edificios 3D
    map.addLayer(
      {
        id: "3d-buildings",
        type: "fill-extrusion",
        source: sourceName,
        "source-layer": "building",
        minzoom: 14.5,
        paint: {
          "fill-extrusion-color": "#6b7280",
          "fill-extrusion-opacity": 0.9,

          // altura con fallback (si no hay render_height)
          "fill-extrusion-height": [
            "interpolate",
            ["linear"],
            ["zoom"],
            14.5, 0,
            16, ["coalesce", ["get", "render_height"], ["get", "height"], 12]
          ],

          // base con fallback
          "fill-extrusion-base": ["coalesce", ["get", "render_min_height"], ["get", "min_height"], 0],
        },
      },
      labelLayerId
    );

    // 4) (Opcional pero recomendado) contorno 2D para que se noten más las siluetas
    map.addLayer(
      {
        id: "building-outline",
        type: "line",
        source: sourceName,
        "source-layer": "building",
        minzoom: 14.5,
        paint: {
          "line-color": "#111827",
          "line-width": 1,
          "line-opacity": 0.35,
        },
      },
      "3d-buildings"
    );
  });
})();