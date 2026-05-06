import { describe, it, expect } from "vitest"
import {
  isUnitAllowed,
  filterAllowedUnits,
  convertAmount,
  pluralizeUnit,
} from "../unitConversion.js"

const u = (id, slug, of) => ({ id, slug, of, name: slug })
const UNITS = {
  g: u(1, "grams", "weight"),
  kg: u(2, "kilograms", "weight"),
  ml: u(3, "milliliter", "volume"),
  l: u(4, "liter", "volume"),
  tsp: u(5, "teaspoon", "volume"),
  tbsp: u(6, "tablespoon", "volume"),
  cup: u(7, "cup", "volume"),
  serving: u(8, "serving", "servings"),
  piece: u(9, "piece", "pieces"),
  clove: u(10, "clove", "pieces"),
  bulb: u(11, "bulb", "pieces"),
}

describe("isUnitAllowed — solid", () => {
  const solid = { state: "solid", name: "mouka" }

  it("allows weight unconditionally", () => {
    expect(isUnitAllowed(UNITS.g, solid)).toBe(true)
    expect(isUnitAllowed(UNITS.kg, solid)).toBe(true)
  })

  it("allows volume only with g_per_liter", () => {
    expect(isUnitAllowed(UNITS.ml, solid)).toBe(false)
    expect(isUnitAllowed(UNITS.cup, { ...solid, g_per_liter: 600 })).toBe(true)
  })

  it("allows piece only with g_per_piece", () => {
    expect(isUnitAllowed(UNITS.piece, solid)).toBe(false)
    expect(isUnitAllowed(UNITS.piece, { ...solid, g_per_piece: 50 })).toBe(true)
  })

  it("allows servings only with g_per_serving", () => {
    expect(isUnitAllowed(UNITS.serving, solid)).toBe(false)
    expect(isUnitAllowed(UNITS.serving, { ...solid, g_per_serving: 250 })).toBe(true)
  })

  it("hides special clove/bulb on non-garlic ingredients", () => {
    expect(isUnitAllowed(UNITS.clove, { ...solid, g_per_piece: 50 })).toBe(false)
    expect(isUnitAllowed(UNITS.bulb, { ...solid, g_per_piece: 50 })).toBe(false)
  })

  it("exposes clove/bulb only for česnek", () => {
    const garlic = { state: "solid", name: "česnek", g_per_piece: 5 }
    expect(isUnitAllowed(UNITS.clove, garlic)).toBe(true)
    expect(isUnitAllowed(UNITS.bulb, garlic)).toBe(true)
  })
})

describe("isUnitAllowed — liquid", () => {
  const liquid = { state: "liquid", name: "olej" }

  it("allows volume unconditionally", () => {
    expect(isUnitAllowed(UNITS.ml, liquid)).toBe(true)
    expect(isUnitAllowed(UNITS.cup, liquid)).toBe(true)
  })

  it("allows weight only with g_per_liter", () => {
    expect(isUnitAllowed(UNITS.g, liquid)).toBe(false)
    expect(isUnitAllowed(UNITS.g, { ...liquid, g_per_liter: 920 })).toBe(true)
  })

  it("requires the full chain to reach piece/serving", () => {
    expect(isUnitAllowed(UNITS.piece, { ...liquid, g_per_piece: 100 })).toBe(false)
    expect(
      isUnitAllowed(UNITS.piece, { ...liquid, g_per_liter: 1000, g_per_piece: 100 }),
    ).toBe(true)
    expect(
      isUnitAllowed(UNITS.serving, {
        ...liquid,
        g_per_liter: 1000,
        g_per_serving: 250,
      }),
    ).toBe(true)
  })
})

describe("convertAmount", () => {
  it("converts within weight directly (no ingredient needed)", () => {
    expect(convertAmount(1.5, UNITS.kg, UNITS.g, { state: "solid" })).toBe(1500)
  })

  it("converts within volume even when liquid lacks g_per_liter", () => {
    expect(convertAmount(2, UNITS.cup, UNITS.ml, { state: "liquid" })).toBe(500)
    expect(convertAmount(15, UNITS.ml, UNITS.tbsp, { state: "liquid" })).toBe(1)
  })

  it("converts cross-group via grams", () => {
    const ing = { state: "solid", g_per_liter: 600 }
    expect(convertAmount(100, UNITS.g, UNITS.ml, ing)).toBeCloseTo(166.667, 2)
  })

  it("converts grams ↔ pieces using g_per_piece", () => {
    const ing = { state: "solid", g_per_piece: 50 }
    expect(convertAmount(150, UNITS.g, UNITS.piece, ing)).toBe(3)
    expect(convertAmount(2, UNITS.piece, UNITS.g, ing)).toBe(100)
  })

  it("uses special factors for česnek's clove", () => {
    const garlic = { state: "solid", name: "česnek", g_per_piece: 5 }
    expect(convertAmount(2, UNITS.clove, UNITS.g, garlic)).toBe(10)
    expect(convertAmount(50, UNITS.g, UNITS.bulb, garlic)).toBe(1)
  })

  it("returns null when conversion chain is missing", () => {
    expect(
      convertAmount(1, UNITS.piece, UNITS.ml, { state: "solid", g_per_piece: 50 }),
    ).toBeNull()
  })
})

describe("pluralizeUnit", () => {
  const gram = { name: "gram", name2: "gramy", name5: "gramů" }

  it("uses singular for 1", () => {
    expect(pluralizeUnit(1, gram)).toBe("gram")
  })
  it("uses plural-2-4 for 2..4 integers", () => {
    expect(pluralizeUnit(2, gram)).toBe("gramy")
    expect(pluralizeUnit(4, gram)).toBe("gramy")
  })
  it("uses plural-5+ for 0, 5+, and decimals", () => {
    expect(pluralizeUnit(0, gram)).toBe("gramů")
    expect(pluralizeUnit(5, gram)).toBe("gramů")
    expect(pluralizeUnit(150, gram)).toBe("gramů")
    expect(pluralizeUnit(1.5, gram)).toBe("gramů")
    expect(pluralizeUnit(2.5, gram)).toBe("gramů")
  })
  it("falls back to singular for nullish amount or missing forms", () => {
    expect(pluralizeUnit(null, gram)).toBe("gram")
    expect(pluralizeUnit(2, { name: "kus" })).toBe("kus")
  })
})

describe("filterAllowedUnits", () => {
  it("keeps only the allowed units for the ingredient", () => {
    const ing = { state: "solid", name: "mouka", g_per_liter: 600 }
    const filtered = filterAllowedUnits(Object.values(UNITS), ing).map(u => u.slug)
    expect(filtered).toContain("grams")
    expect(filtered).toContain("milliliter")
    expect(filtered).toContain("cup")
    expect(filtered).not.toContain("piece")
    expect(filtered).not.toContain("serving")
    expect(filtered).not.toContain("clove")
  })
})
