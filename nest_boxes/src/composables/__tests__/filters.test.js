import { describe, expect, it } from "vitest"

import {
  defaultFilters,
  exportParams,
  filterBoxes,
  filterQuery,
  legendCounts,
  parseFilters,
  seasonStateParams,
} from "@/composables/filters.js"

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
const filtered = overrides =>
  names(filterBoxes(boxes, { ...defaultFilters(), ...overrides }, 2026))

describe("filterBoxes", () => {
  it("leaves out ended boxes by default", () => {
    expect(filtered({})).toEqual(["N10", "N2", "P1"])
  })

  it("filters by the legend, type, verification and the last check", () => {
    expect(filtered({ shown: ["done", "planned"] })).toEqual(["N10", "P1"])
    expect(filtered({ shown: ["ended"] })).toEqual(["Kuba"])
    expect(filtered({ type: [7] })).toEqual(["P1"])
    expect(filtered({ unverified: true })).toEqual(["N2"])
    expect(filtered({ checked: "this_season" })).toEqual(["N10"])
    expect(filtered({ checked: "before" })).toEqual(["N2"])
    expect(filtered({ checked: "never" })).toEqual(["P1"])
  })

  it("searches names without diacritics", () => {
    expect(filtered({ search: "kuba", shown: ["ended"] })).toEqual(["Kuba"])
  })

  it("counts the legend's entries over the other filters", () => {
    const shown = filterBoxes(
      boxes,
      { ...defaultFilters(), shown: [], type: [2] },
      2026,
      { legend: false },
    )
    expect(legendCounts(shown)).toEqual({
      planned: 0,
      to_check: 1,
      attention: 0,
      done: 1,
      ended: 1,
    })
  })
})

describe("the URL", () => {
  it("leaves the defaults out", () => {
    expect(
      Object.values(filterQuery(defaultFilters())).filter(item => item !== undefined),
    ).toEqual([])
    expect(parseFilters({})).toEqual(defaultFilters())
  })

  it("round-trips every filter", () => {
    const filters = {
      unit: 4,
      type: [2, 7],
      shown: ["attention", "ended"],
      unverified: true,
      checked: "never",
      search: "Kuba",
    }
    expect(filterQuery(filters)).toEqual({
      unit: 4,
      type: "2,7",
      states: "attention,ended",
      unverified: "1",
      checked: "never",
      q: "Kuba",
    })
    expect(parseFilters({ ...filterQuery(filters), unit: "4" })).toEqual(filters)
  })

  it("keeps a legend with nothing shown", () => {
    expect(parseFilters(filterQuery({ ...defaultFilters(), shown: [] })).shown).toEqual(
      [],
    )
  })
})

describe("query parameters", () => {
  it("map the filters to the export's query", () => {
    expect(
      exportParams(
        { ...defaultFilters(), unverified: true, checked: "never", type: [2] },
        2026,
      ),
    ).toEqual({
      state: ["planned", "to_check", "attention", "done"],
      type: [2],
      is_verified: false,
      never_checked: true,
    })
    expect(
      exportParams({ ...defaultFilters(), checked: "before" }, 2026),
    ).toMatchObject({ last_checked_before: "2026-07-01" })
  })

  it("leave the legend out of season_states", () => {
    expect(
      seasonStateParams({ ...defaultFilters(), unit: 3, shown: [] }, 2026),
    ).toEqual({ type: [], administration_unit: 3 })
  })
})
