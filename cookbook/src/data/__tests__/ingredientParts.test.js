import { describe, it, expect } from "vitest"
import {
  addPart,
  isPartHeading,
  partHeading,
  withPartHeadings,
  withoutPartHeadings,
} from "../ingredientParts.js"

const describeRows = rows =>
  rows.map(row => (isPartHeading(row) ? `# ${row.name}` : row.id))

describe("withPartHeadings", () => {
  it("leaves an unsplit recipe without headings", () => {
    const rows = withPartHeadings([
      { id: 1, part: "" },
      { id: 2, part: "" },
    ])
    expect(describeRows(rows)).toEqual([1, 2])
  })

  it("puts a heading before each part", () => {
    const rows = withPartHeadings([
      { id: 1, part: "Korpus" },
      { id: 2, part: "Korpus" },
      { id: 3, part: "Krém" },
    ])
    expect(describeRows(rows)).toEqual(["# Korpus", 1, 2, "# Krém", 3])
  })
})

describe("withoutPartHeadings", () => {
  it("assigns each ingredient the part above it and orders them", () => {
    const ingredients = withoutPartHeadings([
      partHeading("Korpus"),
      { id: 1 },
      partHeading("Krém"),
      { id: 2 },
      { id: 3 },
    ])
    expect(ingredients).toEqual([
      { id: 1, part: "Korpus", order: 0 },
      { id: 2, part: "Krém", order: 1 },
      { id: 3, part: "Krém", order: 2 },
    ])
  })

  it("drops a part with no ingredients", () => {
    const ingredients = withoutPartHeadings([
      partHeading("Korpus"),
      { id: 1 },
      partHeading("Poleva"),
    ])
    expect(ingredients.map(i => i.part)).toEqual(["Korpus"])
  })

  it("round-trips withPartHeadings", () => {
    const ingredients = [
      { id: 1, part: "Korpus", order: 0 },
      { id: 2, part: "Krém", order: 1 },
    ]
    expect(withoutPartHeadings(withPartHeadings(ingredients))).toEqual(ingredients)
  })
})

describe("addPart", () => {
  it("turns the existing ingredients into the first part", () => {
    const rows = [{ id: 1 }, { id: 2 }]
    addPart(rows)
    expect(describeRows(rows)).toEqual(["# ", 1, 2, "# "])
  })

  it("only appends once the recipe is split", () => {
    const rows = [partHeading("Korpus"), { id: 1 }]
    addPart(rows)
    expect(describeRows(rows)).toEqual(["# Korpus", 1, "# "])
  })

  it("starts an empty recipe with a single part", () => {
    const rows = []
    addPart(rows)
    expect(describeRows(rows)).toEqual(["# "])
  })
})
