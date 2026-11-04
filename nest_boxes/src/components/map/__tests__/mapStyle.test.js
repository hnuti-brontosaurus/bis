import { describe, expect, it } from "vitest"

import { styleFor } from "@/components/map/mapStyle.js"
import { palettes } from "@/composables/theme.js"

const layer = (id, type, sourceLayer, paint = {}) => ({
  id,
  type,
  source: "openmaptiles",
  "source-layer": sourceLayer,
  paint,
})

const baseStyle = {
  version: 8,
  sources: { openmaptiles: { type: "vector", url: "x", attribution: "OpenMapTiles" } },
  layers: [
    { id: "background", type: "background", paint: { "background-color": "#fff" } },
    layer("water", "fill", "water", { "fill-color": "#fff" }),
    layer("landcover_wood", "fill", "landcover", {
      "fill-color": "#fff",
      "fill-opacity": 0.1,
    }),
    layer("waterway", "line", "waterway", { "line-color": "#fff" }),
    layer("building", "fill", "building", {
      "fill-color": "#fff",
      "fill-outline-color": "#000",
    }),
    layer("highway-path", "line", "transportation", { "line-color": "#fff" }),
    layer("highway-minor-casing", "line", "transportation", { "line-color": "#fff" }),
    layer("highway-primary", "line", "transportation", { "line-color": "#fff" }),
    layer("road_oneway", "symbol", "transportation"),
    layer("highway-shield-non-us", "symbol", "transportation_name", {
      "text-color": "#000",
    }),
    layer("label_city", "symbol", "place", { "text-color": "#000" }),
    layer("label_village", "symbol", "place", { "text-color": "#000" }),
  ],
}

const terrain = {
  nest_boxes_dem: { type: "raster-dem" },
  nest_boxes_contours: { type: "vector" },
}

describe("styleFor", () => {
  const { map } = palettes.dark
  const style = styleFor(baseStyle, palettes.dark, terrain)
  const byId = Object.fromEntries(style.layers.map(item => [item.id, item]))

  it("recolours the layers from the --map-* tokens", () => {
    expect(byId.background.paint["background-color"]).toBe(map.land)
    expect(byId.water.paint["fill-color"]).toBe(map.water)
    expect(byId.landcover_wood.paint["fill-color"]).toBe(map.forest)
    expect(byId.landcover_wood.paint["fill-opacity"]).toBe(1)
    expect(byId.building.paint["fill-outline-color"]).toBe(map.bldLine)
    expect(byId["highway-minor-casing"].paint["line-color"]).toBe(map.roadCase)
    expect(byId["highway-primary"].paint["line-color"]).toBe(map.roadMajor)
    expect(byId.label_city.paint["text-color"]).toBe(map.city)
    expect(byId.label_village.paint["text-color"]).toBe(map.label)
    expect(byId.label_village.paint["text-halo-color"]).toBe(map.land)
  })

  it("names places in Czech where the tiles know the name", () => {
    expect(byId.label_city.layout["text-field"]).toEqual([
      "coalesce",
      ["get", "name:cs"],
      ["get", "name"],
    ])
  })

  it("dashes the paths", () => {
    expect(byId["highway-path"].paint["line-color"]).toBe(map.path)
    expect(byId["highway-path"].paint["line-dasharray"]).toEqual([2, 1.5])
  })

  it("drops one-way arrows and leaves road numbers dark on their shield", () => {
    expect(byId.road_oneway).toBeUndefined()
    expect(byId["highway-shield-non-us"].paint["text-color"]).toBe("#000")
  })

  it("adds fields, hillshade and contours under the roads", () => {
    const ids = style.layers.map(item => item.id)
    expect(ids.slice(3, 7)).toEqual([
      "nest_boxes_field",
      "nest_boxes_forest_outline",
      "nest_boxes_hillshade",
      "nest_boxes_contours",
    ])
    expect(ids[7]).toBe("waterway")
    expect(ids.indexOf("nest_boxes_contour_labels")).toBe(
      ids.indexOf("highway-shield-non-us") - 1,
    )
    expect(style.sources).toMatchObject(terrain)
  })

  it("leaves the attribution to the map", () => {
    expect(style.sources.openmaptiles.attribution).toBe("")
    expect(baseStyle.sources.openmaptiles.attribution).toBe("OpenMapTiles")
  })
})
