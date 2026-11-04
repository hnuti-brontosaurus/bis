import { describe, expect, it } from "vitest"

import {
  describeFigures,
  seasonTable,
  stateBubbles,
  statisticsBubbles,
  unitsOf,
} from "@/composables/statistics.js"

const figures = {
  boxes: 20,
  cleaned: 12,
  inspected: 10,
  occupied: 8,
  bird_occupied: 6,
  previous_inspected: 0,
  previous_occupied: 0,
  done: 10,
  attention: 3,
}

describe("statistics", () => {
  it("derives the ratios from the raw counts", () => {
    expect(describeFigures(figures)).toEqual({
      coverage: 0.6,
      coverageLabel: "60 %",
      occupancyLabel: "80 %",
      birdOccupancyLabel: "60 %",
      previousOccupancyLabel: "–",
    })
  })

  it("lists each unit once, sorted the Czech way", () => {
    const unit = (id, name) => ({ administration_unit: { id, name } })
    expect(
      unitsOf([unit(2, "ZČ Čejkovice"), unit(1, "RC Brno"), unit(2, "ZČ Čejkovice")]),
    ).toEqual([
      { id: 1, name: "RC Brno" },
      { id: 2, name: "ZČ Čejkovice" },
    ])
  })

  it("makes bubbles of the areas with a marker and any boxes", () => {
    const marker = { type: "Point", coordinates: [14, 50] }
    const areas = [
      { id: 1, name: "A", marker },
      { id: 2, name: "B", marker: null },
      { id: 3, name: "C", marker },
    ]
    const rows = [1, 2, 3].map(id => ({ ...figures, area: { id } }))
    rows[2].boxes = 0

    expect(statisticsBubbles(rows, areas)).toEqual([
      { area: areas[0], count: 20, done: 10, attention: 3 },
    ])
    expect(
      stateBubbles(
        [{ area_id: 3, planned: 1, to_check: 2, attention: 3, done: 4 }],
        areas,
      ),
    ).toEqual([{ area: areas[2], count: 10, done: 4, attention: 3 }])
  })

  it("groups the seasons table by unit, with totals", () => {
    const unit = (id, name) => ({ id, name, abbreviation: name })
    const row = (name, administration_unit, inspected) => ({
      area: { id: name, name, administration_unit },
      seasons: inspected.map(count => ({ inspected: count, occupied: 1 })),
    })
    const brno = unit(1, "Brno")
    const table = seasonTable([
      row("Žabovřesky", brno, [2, 3]),
      row("Adamov", unit(2, "Adamov"), [1, 0]),
      row("Bohunice", brno, [4, 5]),
    ])

    expect(table.units.map(group => group.unit.name)).toEqual(["Adamov", "Brno"])
    expect(table.units[1].areas.map(row => row.area.name)).toEqual([
      "Bohunice",
      "Žabovřesky",
    ])
    expect(table.units[1].seasons).toEqual([
      { inspected: 6, occupied: 2 },
      { inspected: 8, occupied: 2 },
    ])
    expect(table.total).toEqual([
      { inspected: 7, occupied: 3 },
      { inspected: 8, occupied: 3 },
    ])
  })
})
