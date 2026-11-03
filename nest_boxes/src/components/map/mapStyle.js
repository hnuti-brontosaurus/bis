const PAINT_COLOR = {
  fill: "fill-color",
  line: "line-color",
  background: "background-color",
}

const PATH_DASH = [2, 1.5]

const colorFor = (layer, map) => {
  const sourceLayer = layer["source-layer"]
  const id = layer.id
  if (layer.type === "background") return map.land
  if (sourceLayer === "water" || sourceLayer === "waterway") return map.water
  if (sourceLayer === "landcover") return id.includes("wood") ? map.forest : map.land
  if (sourceLayer === "park") return map.field
  if (sourceLayer === "landuse") return map.bld
  if (sourceLayer === "building") return map.bld
  if (sourceLayer === "boundary") return map.border
  if (sourceLayer === "aeroway") return id.includes("casing") ? map.roadCase : map.road
  if (sourceLayer === "transportation") {
    if (id.includes("casing")) return map.roadCase
    if (id.includes("path") || id.includes("rail")) return map.path
    return map.road
  }
  return null
}

const NAMED_LAYERS = ["place", "water_name", "waterway"]

const CZECH_NAME = ["coalesce", ["get", "name:cs"], ["get", "name"]]

const restyleSymbol = (layer, colors) => {
  const isCity =
    layer["source-layer"] === "place" && /city|town|country|state/.test(layer.id)
  return {
    ...layer,
    layout: NAMED_LAYERS.includes(layer["source-layer"])
      ? { ...layer.layout, "text-field": CZECH_NAME }
      : layer.layout,
    paint: {
      ...layer.paint,
      "text-color": isCity ? colors.map.city : colors.map.label,
      "text-halo-color": colors.map.land,
    },
  }
}

const restyleLayer = (layer, colors) => {
  if (layer.type === "symbol") return restyleSymbol(layer, colors)
  const color = colorFor(layer, colors.map)
  if (!color) return layer
  const paint = { ...layer.paint, [PAINT_COLOR[layer.type]]: color }
  if (layer.type === "fill" && "fill-outline-color" in paint)
    paint["fill-outline-color"] = color
  if (layer.id === "highway_path") paint["line-dasharray"] = PATH_DASH
  return { ...layer, paint }
}

const fieldLayer = colors => ({
  id: "nest_boxes_field",
  type: "fill",
  source: "openmaptiles",
  "source-layer": "landcover",
  filter: ["in", ["get", "class"], ["literal", ["farmland", "grass"]]],
  paint: { "fill-color": colors.map.field },
})

const forestOutlineLayer = colors => ({
  id: "nest_boxes_forest_outline",
  type: "line",
  source: "openmaptiles",
  "source-layer": "landcover",
  filter: ["==", ["get", "class"], "wood"],
  minzoom: 11,
  paint: { "line-color": colors.map.forestLine, "line-width": 1 },
})

const terrainLayers = colors => [
  {
    id: "nest_boxes_hillshade",
    type: "hillshade",
    source: "nest_boxes_dem",
    paint: {
      "hillshade-shadow-color": colors.shadowC,
      "hillshade-highlight-color": "rgba(0, 0, 0, 0)",
      "hillshade-accent-color": "rgba(0, 0, 0, 0)",
      "hillshade-exaggeration": 0.25,
    },
  },
  {
    id: "nest_boxes_contours",
    type: "line",
    source: "nest_boxes_contours",
    "source-layer": "contours",
    minzoom: 11,
    paint: {
      "line-color": colors.map.contour,
      "line-width": ["match", ["get", "level"], 1, 1, 0.6],
    },
  },
]

const isUnderRoads = layer =>
  ["background", "park", "water", "landcover", "landuse"].includes(
    layer["source-layer"] ?? layer.type,
  )

/**
 * The OpenFreeMap style recoloured from the --map-* tokens, with fields,
 * forest outlines, hillshade and contours added under the roads. Source
 * attributions are dropped: the map shows MAP_ATTRIBUTION instead.
 */
export const styleFor = (baseStyle, colors, terrainSources) => {
  const layers = baseStyle.layers.map(layer => restyleLayer(layer, colors))
  const roadsStart = layers.findIndex(layer => !isUnderRoads(layer))
  const sources = Object.fromEntries(
    Object.entries(baseStyle.sources).map(([name, source]) => [
      name,
      { ...source, attribution: "" },
    ]),
  )
  return {
    ...baseStyle,
    sources: { ...sources, ...terrainSources },
    layers: [
      ...layers.slice(0, roadsStart),
      fieldLayer(colors),
      forestOutlineLayer(colors),
      ...terrainLayers(colors),
      ...layers.slice(roadsStart),
    ],
  }
}
