import { describe, it, expect } from "vitest"
import {
  addPart,
  isPartHeading,
  movePart,
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

describe("movePart", () => {
  const rows = () => [
    partHeading("Korpus"),
    { id: 1 },
    { id: 2 },
    partHeading("Krém"),
    { id: 3 },
    partHeading("Poleva"),
    { id: 4 },
  ]

  it("moves a part up together with its ingredients", () => {
    const moved = rows()
    movePart(moved, 3, "up")
    expect(describeRows(moved)).toEqual(["# Krém", 3, "# Korpus", 1, 2, "# Poleva", 4])
  })

  it("moves a part down together with its ingredients", () => {
    const moved = rows()
    movePart(moved, 0, "down")
    expect(describeRows(moved)).toEqual(["# Krém", 3, "# Korpus", 1, 2, "# Poleva", 4])
  })

  it("moves the first part above the ingredients that have no part", () => {
    const moved = [{ id: 1 }, partHeading("Krém"), { id: 2 }]
    movePart(moved, 1, "up")
    expect(describeRows(moved)).toEqual(["# Krém", 2, 1])
  })

  it("leaves the first part alone when moved up and the last when moved down", () => {
    const moved = rows()
    movePart(moved, 0, "up")
    movePart(moved, 5, "down")
    expect(describeRows(moved)).toEqual(describeRows(rows()))
  })
})
