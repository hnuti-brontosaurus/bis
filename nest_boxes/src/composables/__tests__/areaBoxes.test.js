import { describe, expect, it } from "vitest"

import {
  boxExtras,
  groupByArea,
  markerState,
  splitByBatch,
  withoutReplaced,
} from "@/composables/areaBoxes.js"

const box = (name, overrides = {}) => ({
  id: name,
  name,
  previous_names: "",
  status: "in_use",
  type_id: 2,
  is_verified: true,
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

describe("boxExtras", () => {
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
    expect(boxExtras(box("N1"), check, context)).toEqual([
      "Letos: vyčištěno · sýkora · čeká na potvrzení",
      "Nikdy kontrolovaná",
    ])
  })

  it("says why an unchecked box may need no check", () => {
    expect(boxExtras(box("N1", { type_id: 11 }), null, context)[0]).toBe(
      "Tento typ se nečistí.",
    )
    expect(boxExtras(box("N5"), null, context)[0]).toBe("V obchůzce Podzim B")
    expect(boxExtras(box("P", { status: "planned" }), null, context)).toEqual([])
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

describe("withoutReplaced", () => {
  const at = metresEast => ({
    type: "Point",
    coordinates: [14.4 + metresEast / 71_700, 50],
  })

  it("hides an ended box a current one hangs within 5 m of", () => {
    const replaced = box("Old", { status: "ended", location: at(0) })
    const kept = box("Far", { status: "ended", location: at(30) })
    const current = box("New", { location: at(3) })
    expect(names(withoutReplaced([replaced, kept, current]))).toEqual(["Far", "New"])
  })

  it("looks for the replacement among all boxes, not just the shown ones", () => {
    const replaced = box("Old", { status: "ended", location: at(0) })
    const current = box("New", { status: "planned", location: at(4) })
    expect(withoutReplaced([replaced], [replaced, current])).toEqual([])
  })
})
