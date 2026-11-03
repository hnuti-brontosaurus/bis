import { describe, expect, it } from "vitest"

import { batchHighlights, batchTiles } from "@/composables/batchSummary.js"

const location = { type: "Point", coordinates: [14.36, 50.07] }
const box = { id: "b1", name: "N1", type_id: 1, location }
const check = overrides => ({
  id: overrides.id ?? "c",
  box_id: "b1",
  found: "found",
  cleaning: "cleaned",
  contents: ["nothing"],
  box_left: "fine",
  box_changes: {},
  photos: [],
  note: "",
  ...overrides,
})
const context = {
  boxesById: new Map([["b1", box]]),
  typesById: new Map([
    [1, { name: "malý sýkorník" }],
    [2, { name: "velký sýkorník" }],
  ]),
}

describe("batchTiles", () => {
  it("counts the batch's checks", () => {
    const tiles = batchTiles(
      { box_count: 4 },
      [
        check({ contents: ["bird_nest"], photos: [{}] }),
        check({ cleaning: "not_cleaned" }),
        check({ found: "not_found", cleaning: "", contents: [] }),
        check({ box_left: "needs_repair", contents: ["unknown"] }),
      ],
      [],
    )
    const value = label => tiles.find(tile => tile.label.includes(label)).value
    expect(value("zkontrolováno")).toBe(4)
    expect(value("nalezeno")).toBe(3)
    expect(value("vyčištěno")).toBe(2)
    expect(tiles.find(tile => tile.label.startsWith("obsazeno"))).toMatchObject({
      value: 1,
      label: "obsazeno z 2",
    })
    expect(value("oprava")).toBe(1)
    expect(value("nenalezeno")).toBe(1)
    expect(value("s fotkou")).toBe(1)
  })
})

describe("batchHighlights", () => {
  it("flags what needs a look", () => {
    const moved = { type: "Point", coordinates: [14.3606, 50.07] }
    const titles = batchHighlights(
      [
        check({ id: "1", found: "not_found", note: "spadla" }),
        check({ id: "2", box_left: "needs_replacing" }),
        check({ id: "3", box_changes: { type: 2, location: moved } }),
        check({ id: "4", box_changes: { type: 1 } }),
      ],
      [{ id: "new", name: "N9" }],
      context,
    ).map(item => item.title)
    expect(titles).toEqual([
      "Nová budka",
      "Nenalezena",
      "potřebuje vyměnit",
      "Typ změněn",
      "Poloha posunuta o 43 m",
    ])
  })
})
