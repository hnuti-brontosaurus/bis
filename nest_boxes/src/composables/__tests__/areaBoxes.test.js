import { describe, expect, it } from "vitest"

import {
  boxRowDetail,
  groupByArea,
  markerState,
  splitByBatch,
} from "@/composables/areaBoxes.js"

const box = (name, overrides = {}) => ({
  id: name,
  name,
  previous_names: "",
  status: "in_use",
  type_id: 2,
  is_verified: true,
  condition: "fine",
  last_checked_on: null,
  ...overrides,
})

const boxes = [
  box("N10", { last_checked_on: "2026-10-01", season_state: "done" }),
  box("N2", {
    last_checked_on: "2025-10-01",
    is_verified: false,
    season_state: "to_check",
  }),
  box("Kuba", { status: "ended", season_state: null }),
  box("P1", { status: "planned", type_id: 7, season_state: "planned" }),
]
const names = list => list.map(item => item.name)

describe("splitByBatch", () => {
  it("puts the batch's boxes first, each part by name", () => {
    const { inBatch, outside } = splitByBatch(boxes, { box_ids: ["N2", "N10"] })
    expect(names(inBatch)).toEqual(["N2", "N10"])
    expect(names(outside)).toEqual(["Kuba", "P1"])
  })

  it("puts everything outside without a batch", () => {
    expect(splitByBatch(boxes, undefined).inBatch).toEqual([])
  })
})

describe("markerState", () => {
  const batch = { box_ids: ["N10"] }
  it("shows boxes outside the batch as such", () => {
    expect(markerState(boxes[1], batch)).toBe("out")
  })

  it("shows the season state of the rest", () => {
    expect(markerState(boxes[0], batch)).toBe("done")
    expect(markerState(boxes[1], null)).toBe("to_check")
    expect(markerState(boxes[2], null)).toBe("out")
  })
})

describe("boxRowDetail", () => {
  const context = {
    typesById: new Map([
      [2, { id: 2, name: "velký sýkorník", needs_cleaning: true }],
      [11, { id: 11, name: "netopýrník", needs_cleaning: false }],
    ]),
    occupantsById: new Map([[1, { id: 1, name: "sýkora" }]]),
    otherBatches: [{ name: "Podzim B", box_ids: ["N5"] }],
  }

  it("says what the check found and that it waits", () => {
    const check = {
      found: "found",
      cleaning: "cleaned",
      contents: ["bird_nest"],
      occupant_ids: [1],
      box_left: "fine",
      box_changes: {},
      is_confirmed: false,
    }
    expect(boxRowDetail(box("N1"), check, context).text).toBe(
      "velký sýkorník · vyčištěno · sýkora · čeká",
    )
  })

  it("says why an unchecked box may need no check", () => {
    expect(boxRowDetail(box("N1", { type_id: 11 }), null, context)).toEqual({
      text: "netopýrník · nečistí se",
      tone: "info",
    })
    expect(boxRowDetail(box("N5"), null, context).text).toBe(
      "velký sýkorník · v obchůzce Podzim B",
    )
    expect(
      boxRowDetail(box("N6", { condition: "needs_replacing" }), null, context).tone,
    ).toBe("bad")
  })
})

describe("groupByArea", () => {
  it("groups by area, both by name", () => {
    const areasById = new Map([
      [1, { id: 1, name: "Žabovřesky" }],
      [2, { id: 2, name: "Cibulka" }],
    ])
    const groups = groupByArea(
      [box("10", { area_id: 1 }), box("2", { area_id: 2 }), box("9", { area_id: 1 })],
      areasById,
    )
    expect(
      groups.map(group => [group.title, group.boxes.map(item => item.name)]),
    ).toEqual([
      ["Cibulka", ["2"]],
      ["Žabovřesky", ["9", "10"]],
    ])
  })
})
