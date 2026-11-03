import { describe, expect, it } from "vitest"

import {
  boxRowDetail,
  defaultFilters,
  filterBoxes,
  filterParams,
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
  is_confirmed: true,
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
const filtered = overrides =>
  names(filterBoxes(boxes, { ...defaultFilters(), ...overrides }, 2026))

describe("filterBoxes", () => {
  it("leaves out ended boxes by default", () => {
    expect(filtered({})).toEqual(["N10", "N2", "P1"])
  })

  it("filters by type, season state, verification and the last check", () => {
    expect(filtered({ state: ["done", "planned"] })).toEqual(["N10", "P1"])
    expect(filtered({ type: [7] })).toEqual(["P1"])
    expect(filtered({ unverified: true })).toEqual(["N2"])
    expect(filtered({ checked: "this_season" })).toEqual(["N10"])
    expect(filtered({ checked: "before" })).toEqual(["N2"])
    expect(filtered({ checked: "never" })).toEqual(["P1"])
  })

  it("searches names without diacritics", () => {
    expect(filtered({ search: "kuba", status: [] })).toEqual(["Kuba"])
  })
})

describe("filterParams", () => {
  it("maps the filters to the export's query", () => {
    expect(
      filterParams(
        { ...defaultFilters(), unverified: true, checked: "never", type: [2] },
        2026,
      ),
    ).toEqual({
      status: ["planned", "in_use", "taken_down", "missing"],
      season_state: [],
      type: [2],
      is_verified: false,
      never_checked: true,
    })
    expect(
      filterParams({ ...defaultFilters(), checked: "before" }, 2026),
    ).toMatchObject({
      last_checked_before: "2026-07-01",
    })
  })
})

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
      "velký sýkorník · v dávce Podzim B",
    )
    expect(
      boxRowDetail(box("N6", { condition: "needs_replacing" }), null, context).tone,
    ).toBe("bad")
  })
})
