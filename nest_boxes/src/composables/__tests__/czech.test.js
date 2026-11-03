import { describe, expect, it } from "vitest"

import {
  areaCountLabel,
  boxCountLabel,
  currentSeason,
  pendingLabel,
  percent,
  seasonLabel,
} from "@/composables/czech.js"

describe("czech", () => {
  it("picks the plural form", () => {
    expect(pendingLabel(1)).toBe("1 čeká")
    expect(pendingLabel(2)).toBe("2 čekají")
    expect(pendingLabel(5)).toBe("5 čeká")
    expect(areaCountLabel(3)).toBe("3 oblasti")
    expect(areaCountLabel(12)).toBe("12 oblastí")
    expect(boxCountLabel(1)).toBe("1 budka")
  })

  it("formats thousands the Czech way", () => {
    expect(boxCountLabel(1135)).toBe("1 135 budek")
  })

  it("shows a dash for a ratio of nothing", () => {
    expect(percent(1, 3)).toBe("33 %")
    expect(percent(0, 0)).toBe("–")
  })

  it("starts the season on 1 July", () => {
    expect(currentSeason(new Date(2026, 5, 30))).toBe(2025)
    expect(currentSeason(new Date(2026, 6, 1))).toBe(2026)
    expect(seasonLabel(2026)).toBe("2026/27")
    expect(seasonLabel(2099)).toBe("2099/00")
  })
})
