import { describe, expect, it, vi } from "vitest"

import {
  fetchAll,
  glyphUrls,
  spriteUrls,
  tileOf,
  tilesInBounds,
  tileUrls,
  withMargin,
} from "@/components/map/prefetch.js"

describe("tile math", () => {
  it("finds the tile of a point", () => {
    expect(tileOf([0, 0], 0)).toEqual({ x: 0, y: 0 })
    expect(tileOf([0, 0], 1)).toEqual({ x: 1, y: 1 })
    // Prague at zoom 14, as OSM numbers it
    expect(tileOf([14.42, 50.087], 14)).toEqual({ x: 8848, y: 5550 })
  })

  it("lists every tile of the bounds", () => {
    const bounds = [
      [14.36, 50.06],
      [14.38, 50.08],
    ]
    const tiles = tilesInBounds(bounds, 14)
    const { x: west, y: north } = tileOf([14.36, 50.08], 14)
    const { x: east, y: south } = tileOf([14.38, 50.06], 14)
    expect(tiles).toHaveLength((east - west + 1) * (south - north + 1))
    expect(tiles[0]).toEqual({ z: 14, x: west, y: north })
  })

  it("widens bounds by metres on every side", () => {
    const [[west, south], [east, north]] = withMargin(
      [
        [14.36, 50.07],
        [14.36, 50.07],
      ],
      1000,
    )
    expect((north - south) * 111_320).toBeCloseTo(2000, 0)
    expect((east - west) * 111_320 * Math.cos((50.07 * Math.PI) / 180)).toBeCloseTo(
      2000,
      0,
    )
  })
})

describe("tileUrls", () => {
  const bounds = [
    [14.3, 50.0],
    [14.5, 50.1],
  ]
  const sources = [
    { template: "https://tiles/{z}/{x}/{y}.pbf", minzoom: 0, maxzoom: 14 },
    { template: "https://dem/{z}/{x}/{y}.png", minzoom: 0, maxzoom: 12 },
  ]

  it("fills each source's template up to its own maximum zoom", () => {
    const urls = tileUrls(sources, bounds, 3000)
    expect(urls[0]).toBe("https://tiles/0/0/0.pbf")
    expect(urls[1]).toBe("https://dem/0/0/0.png")
    expect(urls.some(url => url.startsWith("https://tiles/14/"))).toBe(true)
    expect(urls.some(url => url.startsWith("https://dem/13/"))).toBe(false)
  })

  it("leaves out whole zoom levels that would go over the cap", () => {
    const all = tileUrls(sources, bounds, 3000)
    const capped = tileUrls(sources, bounds, all.length - 1)
    expect(capped.length).toBeLessThan(all.length)
    expect(capped.some(url => url.startsWith("https://tiles/14/"))).toBe(false)
    expect(capped).toEqual(all.slice(0, capped.length))
  })
})

describe("style files", () => {
  const style = {
    glyphs: "https://tiles/fonts/{fontstack}/{range}.pbf",
    sprite: "https://tiles/sprites/ofm",
    layers: [
      { id: "a", layout: { "text-font": ["Noto Sans Regular"] } },
      { id: "b", layout: { "text-font": ["Noto Sans Regular"] } },
      { id: "c", layout: { "text-font": ["Noto Sans Bold", "Noto Sans Regular"] } },
      { id: "d", layout: {} },
    ],
  }

  it("asks for the Czech glyph ranges of every font stack once", () => {
    const urls = glyphUrls(style)
    expect(urls).toHaveLength(6)
    expect(urls).toContain("https://tiles/fonts/Noto Sans Regular/256-511.pbf")
    expect(urls).toContain(
      "https://tiles/fonts/Noto Sans Bold,Noto Sans Regular/0-255.pbf",
    )
  })

  it("picks the sprite for the screen", () => {
    expect(spriteUrls(style, 2)).toEqual([
      "https://tiles/sprites/ofm@2x.json",
      "https://tiles/sprites/ofm@2x.png",
    ])
    expect(spriteUrls(style, 1)).toEqual([
      "https://tiles/sprites/ofm.json",
      "https://tiles/sprites/ofm.png",
    ])
  })
})

describe("fetchAll", () => {
  it("keeps at most `parallel` requests open and counts the failures", async () => {
    let open = 0
    let most = 0
    vi.stubGlobal("fetch", async url => {
      most = Math.max(most, ++open)
      await new Promise(resolve => setTimeout(resolve, 1))
      open--
      if (url === "bad") throw new TypeError("Failed to fetch")
      return { ok: url !== "missing" }
    })
    const progress = vi.fn()
    const urls = ["a", "b", "bad", "c", "missing", "d", "e", "f", "g"]

    expect(await fetchAll(urls, { parallel: 4, onProgress: progress })).toBe(2)
    expect(most).toBe(4)
    expect(progress).toHaveBeenLastCalledWith(urls.length, urls.length)
    vi.unstubAllGlobals()
  })
})
