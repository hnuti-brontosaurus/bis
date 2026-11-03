import { describe, expect, it } from "vitest"

import { describeFigures, recentSeasons, unitsOf } from "@/composables/statistics.js"

const figures = {
  boxes: 20,
  cleaned: 12,
  inspected: 10,
  occupied: 8,
  bird_occupied: 6,
  previous_inspected: 0,
  previous_occupied: 0,
  to_repair: 1,
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

  it("lists seasons newest first", () => {
    expect(recentSeasons(2026, 3)).toEqual([2026, 2025, 2024])
  })
})
