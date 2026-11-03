import { loadBaseStyle } from "@/components/map/baseStyle.js"
import { boundsOf } from "@/components/map/geometry.js"
import { DEM_MAX_ZOOM, DEM_TILES_URL } from "@/config.js"

// OpenFreeMap's terms for one download: at most 3,000 tiles, 4 requests at once
export const MAX_TILES = 3000
export const PARALLEL_REQUESTS = 4

const MARGIN_METRES = 1000
const METRES_PER_DEGREE = 111_320
// Basic Latin, Latin Extended-A (Czech) and general punctuation
const GLYPH_RANGES = ["0-255", "256-511", "8192-8447"]
const TILE_SOURCE_TYPES = ["vector", "raster", "raster-dem"]
// maplibre's own default for a source that names none
const DEFAULT_MAX_ZOOM = 22

/** @typedef {[[number, number], [number, number]]} Bounds [[west, south], [east, north]] */

/** @returns {Bounds} */
export const withMargin = ([[west, south], [east, north]], metres) => {
  const latitude = (((south + north) / 2) * Math.PI) / 180
  const latitudeDelta = metres / METRES_PER_DEGREE
  const longitudeDelta = metres / (METRES_PER_DEGREE * Math.cos(latitude))
  return [
    [west - longitudeDelta, south - latitudeDelta],
    [east + longitudeDelta, north + latitudeDelta],
  ]
}

export const tileOf = ([lng, lat], zoom) => {
  const count = 2 ** zoom
  const latitude = (lat * Math.PI) / 180
  const clamp = value => Math.min(count - 1, Math.max(0, Math.floor(value)))
  return {
    x: clamp(((lng + 180) / 360) * count),
    y: clamp(((1 - Math.asinh(Math.tan(latitude)) / Math.PI) / 2) * count),
  }
}

export const tilesInBounds = ([[west, south], [east, north]], zoom) => {
  const topLeft = tileOf([west, north], zoom)
  const bottomRight = tileOf([east, south], zoom)
  const tiles = []
  for (let x = topLeft.x; x <= bottomRight.x; x++)
    for (let y = topLeft.y; y <= bottomRight.y; y++) tiles.push({ z: zoom, x, y })
  return tiles
}

export const fillTemplate = (template, { z, x, y }) =>
  template.replace("{z}", z).replace("{x}", x).replace("{y}", y)

/**
 * The tile URLs of `sources` ([{template, minzoom, maxzoom}]) covering `bounds`,
 * zoom by zoom from the lowest. A zoom level that would go over `limit` is left
 * out whole, so the cap costs the finest detail and never a hole in the map.
 */
export const tileUrls = (sources, bounds, limit) => {
  const urls = []
  const maxZoom = Math.max(...sources.map(source => source.maxzoom))
  for (let zoom = 0; zoom <= maxZoom; zoom++) {
    const level = sources
      .filter(source => source.minzoom <= zoom && zoom <= source.maxzoom)
      .flatMap(source =>
        tilesInBounds(bounds, zoom).map(tile => fillTemplate(source.template, tile)),
      )
    if (urls.length + level.length > limit) break
    urls.push(...level)
  }
  return urls
}

const fontStacks = style => [
  ...new Set(
    style.layers
      .map(layer => layer.layout?.["text-font"])
      .filter(
        fonts => Array.isArray(fonts) && fonts.every(font => typeof font === "string"),
      )
      .map(fonts => fonts.join(",")),
  ),
]

export const glyphUrls = style =>
  fontStacks(style).flatMap(stack =>
    GLYPH_RANGES.map(range =>
      style.glyphs.replace("{fontstack}", stack).replace("{range}", range),
    ),
  )

export const spriteUrls = (style, pixelRatio) => {
  const suffix = pixelRatio > 1 ? "@2x" : ""
  const sprites =
    typeof style.sprite === "string" ? [{ url: style.sprite }] : style.sprite
  return sprites.flatMap(({ url }) => [`${url}${suffix}.json`, `${url}${suffix}.png`])
}

const tileSource = async source => {
  const tileJson = source.url
    ? await fetch(source.url).then(response => response.json())
    : source
  return {
    template: tileJson.tiles[0],
    minzoom: tileJson.minzoom ?? 0,
    maxzoom: tileJson.maxzoom ?? DEFAULT_MAX_ZOOM,
  }
}

/** Everything the map needs to draw `points` and their surroundings offline. */
export const mapUrls = async (style, points, pixelRatio) => {
  const sources = await Promise.all(
    Object.values(style.sources)
      .filter(source => TILE_SOURCE_TYPES.includes(source.type))
      .map(tileSource),
  )
  sources.push({ template: DEM_TILES_URL, minzoom: 0, maxzoom: DEM_MAX_ZOOM })
  const bounds = withMargin(boundsOf(points), MARGIN_METRES)
  return [
    ...glyphUrls(style),
    ...spriteUrls(style, pixelRatio),
    ...tileUrls(sources, bounds, MAX_TILES),
  ]
}

/**
 * Fetches `urls` at most `parallel` at a time. The service worker answers
 * them cache-first and keeps what it fetched, so this both fills the cache
 * and skips what is already there. Resolves to the number that failed.
 */
export const fetchAll = async (urls, { parallel, onProgress }) => {
  let next = 0
  let done = 0
  let failed = 0
  const worker = async () => {
    while (next < urls.length) {
      const url = urls[next++]
      const ok = await fetch(url).then(
        response => response.ok,
        () => false,
      )
      if (!ok) failed++
      onProgress(++done, urls.length)
    }
  }
  await Promise.all(Array.from({ length: parallel }, worker))
  return failed
}

// Until the freshly installed service worker claims the page, its fetches
// bypass it and nothing lands in the cache.
const serviceWorkerControl = () =>
  navigator.serviceWorker.controller ||
  new Promise(resolve =>
    navigator.serviceWorker.addEventListener("controllerchange", resolve, {
      once: true,
    }),
  )

export const prefetchMap = async (points, onProgress) => {
  if (import.meta.env.PROD) await serviceWorkerControl()
  const urls = await mapUrls(await loadBaseStyle(), points, window.devicePixelRatio)
  return fetchAll(urls, { parallel: PARALLEL_REQUESTS, onProgress })
}
