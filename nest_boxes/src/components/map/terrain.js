import { addProtocol } from "maplibre-gl"
import mlcontour from "maplibre-contour"

import { DEM_MAX_ZOOM, DEM_TILES_URL } from "@/config.js"

let sources = null

export const terrainSources = () => {
  if (sources) return sources
  const demSource = new mlcontour.DemSource({
    url: DEM_TILES_URL,
    encoding: "terrarium",
    maxzoom: DEM_MAX_ZOOM,
    worker: true,
  })
  demSource.setupMaplibre({ addProtocol })
  sources = {
    nest_boxes_dem: {
      type: "raster-dem",
      encoding: "terrarium",
      tiles: [demSource.sharedDemProtocolUrl],
      maxzoom: DEM_MAX_ZOOM,
      tileSize: 256,
    },
    nest_boxes_contours: {
      type: "vector",
      tiles: [
        demSource.contourProtocolUrl({
          thresholds: { 11: [50, 250], 13: [20, 100], 15: [10, 50] },
          contourLayer: "contours",
          elevationKey: "ele",
          levelKey: "level",
        }),
      ],
      maxzoom: 15,
    },
  }
  return sources
}
