import { describe, expect, it } from "vitest"

import {
  clampHeight,
  nearestStop,
  nextStopOnTap,
  sheetHeights,
} from "@/components/map/sheet.js"

const heights = sheetHeights(1000, 90)

describe("bottom sheet", () => {
  it("has a collapsed, half and full height", () => {
    expect(heights).toEqual({ collapsed: 90, half: 550, full: 920 })
  })

  it("snaps a drag to the nearest stop", () => {
    expect(nearestStop(heights, 200)).toBe("collapsed")
    expect(nearestStop(heights, 700)).toBe("half")
    expect(nearestStop(heights, 800)).toBe("full")
  })

  it("never drags past the stops", () => {
    expect(clampHeight(heights, 10)).toBe(90)
    expect(clampHeight(heights, 2000)).toBe(920)
  })

  it("opens a collapsed sheet on tap and collapses an open one", () => {
    expect(nextStopOnTap("collapsed")).toBe("half")
    expect(nextStopOnTap("full")).toBe("collapsed")
  })
})
