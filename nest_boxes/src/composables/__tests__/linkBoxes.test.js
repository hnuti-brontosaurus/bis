import { describe, expect, it } from "vitest"

import {
  duplicateNames,
  latestChecks,
  sortBoxes,
  spacingWarnings,
} from "@/composables/linkBoxes.js"

const point = (lng, lat) => ({ type: "Point", coordinates: [lng, lat] })

// About 7.2 m per 0.0001° of longitude at 50° N
const box = (name, lngOffset, extra = {}) => ({
  id: name,
  name,
  location: point(14.36 + lngOffset, 50.07),
  status: "in_use",
  is_confirmed: true,
  type_id: 1,
  ...extra,
})

describe("sortBoxes", () => {
  const boxes = [box("10", 0.003), box("2", 0.001), box("1", 0.002)]

  it("puts the nearest box first", () => {
    expect(sortBoxes(boxes, point(14.36, 50.07)).map(item => item.name)).toEqual([
      "2",
      "1",
      "10",
    ])
  })

  it("sorts by name, numbers as numbers, without a position", () => {
    expect(sortBoxes(boxes, null).map(item => item.name)).toEqual(["1", "2", "10"])
  })
})

describe("latestChecks", () => {
  it("keeps the check made later for each box", () => {
    const checks = latestChecks([
      { id: "a", box_id: "1", made_at: "2026-11-03T12:00:00Z" },
      { id: "b", box_id: "1", made_at: "2026-11-03T09:00:00Z" },
      { id: "c", box_id: "2", made_at: "2026-11-03T08:00:00Z" },
    ])
    expect(checks.get("1").id).toBe("a")
    expect(checks.get("2").id).toBe("c")
  })
})

describe("spacingWarnings", () => {
  const here = point(14.36, 50.07)

  it("warns about any box within 15 m and a same type box within 50 m", () => {
    const boxes = [
      box("other type near", 0.0001, { type_id: 2 }),
      box("other type far", 0.0003, { type_id: 2 }),
      box("same type", 0.0005),
      box("same type far", 0.0008),
    ]
    const warnings = spacingWarnings(boxes, here, 1, null)
    expect(warnings.map(warning => warning.box.name)).toEqual([
      "other type near",
      "same type",
    ])
    expect(warnings.map(warning => warning.shouldBeMoved)).toEqual([false, false])
  })

  it("says when the spot is inside the limits for existing boxes", () => {
    const [close, sameType] = spacingWarnings(
      [box("close", 0.00005, { type_id: 2 }), box("same", 0.0001)],
      here,
      1,
      null,
    )
    expect(close.shouldBeMoved).toBe(true)
    expect(sameType.shouldBeMoved).toBe(true)
  })

  it("leaves out the box itself and boxes not in use", () => {
    const boxes = [
      box("itself", 0),
      box("planned", 0.00001, { status: "planned" }),
      box("unconfirmed", 0.00001, { is_confirmed: false }),
    ]
    expect(spacingWarnings(boxes, here, 1, "itself")).toEqual([])
  })
})

describe("duplicateNames", () => {
  it("matches names in use regardless of case and spaces", () => {
    const boxes = [box("N031", 0), box("n032", 0, { status: "ended" })]
    expect(duplicateNames(boxes, " n031 ", null).map(item => item.id)).toEqual(["N031"])
    expect(duplicateNames(boxes, "N032", null)).toEqual([])
    expect(duplicateNames(boxes, "N031", "N031")).toEqual([])
  })
})
