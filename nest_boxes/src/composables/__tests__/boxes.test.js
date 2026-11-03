import { describe, expect, it } from "vitest"

import {
  boxChangesLabel,
  checkResult,
  describeChange,
  reportedState,
} from "@/composables/boxes.js"

const typesById = new Map([[2, { name: "velký sýkorník" }]])

describe("checkResult", () => {
  const occupantsById = new Map([[1, { name: "sýkora koňadra" }]])
  const check = overrides => ({
    found: "found",
    cleaning: "cleaned",
    contents: ["bird_nest"],
    occupant_ids: [1],
    box_left: "needs_repair",
    box_changes: {},
    ...overrides,
  })

  it("names the occupants and the repair", () => {
    expect(checkResult(check(), occupantsById)).toBe(
      "vyčištěno · sýkora koňadra · potřebuje opravu",
    )
  })

  it("says empty, unknown and not found", () => {
    expect(
      checkResult(
        check({ contents: ["nothing"], occupant_ids: [], box_left: "fine" }),
        occupantsById,
      ),
    ).toBe("vyčištěno · prázdná")
    expect(checkResult(check({ found: "not_found" }), occupantsById)).toBe("nenalezena")
    expect(checkResult(check({ box_changes: { hung: true } }), occupantsById)).toBe(
      "pověšena",
    )
  })
})

describe("describeChange", () => {
  const context = { typesById, endReasonsById: new Map() }

  it("names choices, types and moves", () => {
    expect(describeChange("status", ["in_use", "missing"], context)).toBe(
      "stav vyvěšená → nenalezená",
    )
    expect(describeChange("type", [null, 2], context)).toBe("typ – → velký sýkorník")
    expect(
      describeChange(
        "location",
        [
          [14.36, 50.07],
          [14.3606, 50.07],
        ],
        context,
      ),
    ).toBe("poloha posunuta o 43 m")
  })
})

describe("boxChangesLabel", () => {
  it("summarises the proposed changes", () => {
    expect(boxChangesLabel({ hole_size: 36, type: 2 }, typesById)).toBe(
      "otvor 36 mm, typ velký sýkorník",
    )
    expect(
      boxChangesLabel(
        {
          name: "1",
          location: {},
          hole_shape: "round",
          hole_size: 33,
          type: 2,
          opening: "front",
        },
        typesById,
      ),
    ).toBe("ověření údajů")
  })
})

describe("reportedState", () => {
  const check = overrides => ({
    found: "found",
    cleaning: "cleaned",
    box_left: "fine",
    ...overrides,
  })

  it("is done for a cleaned box left fine", () => {
    expect(reportedState(check({}))).toBe("done")
    expect(reportedState(check({ cleaning: "", box_left: "" }))).toBe("done")
  })

  it("needs attention for what the box needs next", () => {
    expect(reportedState(check({ found: "not_found", cleaning: "" }))).toBe("attention")
    expect(reportedState(check({ cleaning: "could_not_open" }))).toBe("attention")
    expect(reportedState(check({ box_left: "taken_down" }))).toBe("attention")
  })

  it("changes nothing when the box was not reached", () => {
    expect(reportedState(check({ found: "not_reached" }))).toBeNull()
  })
})
