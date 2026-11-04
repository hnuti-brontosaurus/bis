const PAINT_COLOR = {
  fill: "fill-color",
  line: "line-color",
  background: "background-color",
}

const PATH_DASH = [2, 1.5]

const MAJOR_ROAD = /motorway|trunk|primary|secondary|tertiary/

const transportationColor = (id, map) => {
  if (/path|ferry|cablecar/.test(id)) return map.path
  if (id.includes("rail")) return map.rail
  if (id.includes("casing"))
    return MAJOR_ROAD.test(id) ? map.roadMajorCase : map.roadCase
  return MAJOR_ROAD.test(id) ? map.roadMajor : map.road
}

const colorFor = (layer, map) => {
  const sourceLayer = layer["source-layer"]
  const id = layer.id
  if (layer.type === "background") return map.land
  if (sourceLayer === "water" || sourceLayer === "waterway") return map.water
  if (sourceLayer === "landcover") {
    if (id.includes("wood")) return map.forest
    return id.includes("grass") ? map.field : map.land
  }
  if (sourceLayer === "park") return map.field
  if (sourceLayer === "landuse") return map.settlement
  if (sourceLayer === "building") return map.bld
  if (sourceLayer === "boundary") return map.border
  if (sourceLayer === "aeroway") return id.includes("casing") ? map.roadCase : map.road
  if (sourceLayer === "transportation") return transportationColor(id, map)
  return null
}

// One-way arrows and the fake 3D building tops only add noise at our zooms
const DROPPED_LAYERS = ["road_oneway", "road_oneway_opposite", "building-top"]

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

// Road numbers sit on the sprite's white shield, so they keep their dark text
const isShield = layer => layer.id.includes("shield")

const restyleLayer = (layer, colors) => {
  if (isShield(layer)) return layer
  if (layer.type === "symbol") return restyleSymbol(layer, colors)
  const color = colorFor(layer, colors.map)
  if (!color) return layer
  const paint = { ...layer.paint, [PAINT_COLOR[layer.type]]: color }
  if (layer.type === "fill") {
    // The base style tints forests with a nearly transparent fill
    paint["fill-opacity"] = 1
    if ("fill-outline-color" in paint)
      paint["fill-outline-color"] =
        layer["source-layer"] === "building" ? colors.map.bldLine : color
  }
  if (layer.type === "line" && /path/.test(layer.id) && !layer.id.includes("casing"))
    paint["line-dasharray"] = PATH_DASH
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

const INDEX_CONTOUR = ["==", ["get", "level"], 1]

const terrainLayers = colors => [
  {
    id: "nest_boxes_hillshade",
    type: "hillshade",
    source: "nest_boxes_dem",
    paint: {
      "hillshade-shadow-color": colors.shadowC,
      "hillshade-highlight-color": "rgba(0, 0, 0, 0)",
      "hillshade-accent-color": "rgba(0, 0, 0, 0)",
      "hillshade-exaggeration": 0.35,
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
      "line-width": ["case", INDEX_CONTOUR, 1.3, 0.7],
      "line-opacity": ["case", INDEX_CONTOUR, 1, 0.7],
    },
  },
]

const contourLabelLayer = colors => ({
  id: "nest_boxes_contour_labels",
  type: "symbol",
  source: "nest_boxes_contours",
  "source-layer": "contours",
  minzoom: 13,
  filter: INDEX_CONTOUR,
  layout: {
    "symbol-placement": "line",
    "text-field": ["concat", ["get", "ele"], " m"],
    "text-font": ["Noto Sans Regular"],
    "text-size": 10,
    "text-padding": 20,
  },
  paint: {
    "text-color": colors.map.contourLabel,
    "text-halo-color": colors.map.land,
    "text-halo-width": 1.5,
  },
})

const isUnderRoads = layer =>
  ["background", "park", "water", "landcover", "landuse"].includes(
    layer["source-layer"] ?? layer.type,
  )

/**
 * The OpenFreeMap style recoloured from the --map-* tokens, with fields,
 * forest outlines, hillshade and contours added under the roads and the
 * contours' heights under the other labels. Source
 * attributions are dropped: the map shows MAP_ATTRIBUTION instead.
 */
export const styleFor = (baseStyle, colors, terrainSources) => {
  const layers = baseStyle.layers
    .filter(layer => !DROPPED_LAYERS.includes(layer.id))
    .map(layer => restyleLayer(layer, colors))
  const roadsStart = layers.findIndex(layer => !isUnderRoads(layer))
  const labelsStart = layers.findIndex(layer => layer.type === "symbol")
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
      ...layers.slice(roadsStart, labelsStart),
      contourLabelLayer(colors),
      ...layers.slice(labelsStart),
    ],
  }
}
