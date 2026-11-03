import { describe, expect, it } from "vitest"

import {
  buildPayload,
  initialState,
  suggestType,
  typeHint,
  validate,
  VERIFICATION_FIELDS,
} from "@/components/check/checkForm.js"

const types = [
  {
    id: 1,
    name: "malý sýkorník",
    needs_cleaning: true,
    hole_shape: "round",
    hole_min: 27,
    hole_max: 31,
    official_hole_min: 27,
    official_hole_max: 28,
  },
  {
    id: 2,
    name: "velký sýkorník",
    needs_cleaning: true,
    hole_shape: "round",
    hole_min: 32,
    hole_max: 44,
    official_hole_min: 33,
    official_hole_max: 34,
  },
  {
    id: 7,
    name: "lejskovník",
    needs_cleaning: true,
    hole_shape: "oval",
    hole_min: null,
    hole_max: null,
    official_hole_min: null,
    official_hole_max: null,
  },
  {
    id: 11,
    name: "netopýrník",
    needs_cleaning: false,
    hole_shape: "",
    hole_min: null,
    hole_max: null,
    official_hole_min: null,
    official_hole_max: null,
  },
]
const occupants = [
  { id: 1, name: "sýkora", is_bird: true },
  { id: 18, name: "vosy", is_bird: false },
  { id: 27, name: "nevím", is_bird: false },
]
const categories = { types, occupants, not_cleaned_reasons: [] }
const location = { type: "Point", coordinates: [14.36, 50.07] }
const box = {
  id: "box-1",
  name: "N034",
  status: "in_use",
  location,
  type_id: 2,
  hole_shape: "round",
  hole_size: 33,
  opening: "front",
  material: "",
  installed_on: "2020-03-01",
  is_verified: true,
}
const planned = { ...box, status: "planned", installed_on: null, is_verified: false }

const fresh = (overrides = {}, of = box) => ({
  ...initialState(of, null, types, "2026-11-03"),
  ...overrides,
})

describe("suggestType", () => {
  it("picks the type whose range holds the hole", () => {
    expect(suggestType(types, "round", 30).id).toBe(1)
    expect(suggestType(types, "round", 33).id).toBe(2)
  })

  it("matches an unsized shape only to a type without a range", () => {
    expect(suggestType(types, "oval", null).id).toBe(7)
    expect(suggestType(types, "round", null)).toBeNull()
    expect(suggestType(types, "", 33)).toBeNull()
  })
})

describe("typeHint", () => {
  it("says the type follows from the hole", () => {
    expect(typeHint(types[1], "round", 33)).toEqual({
      tone: "ok",
      text: "podle otvoru 32–44 mm",
    })
  })

  it("warns when the hole is outside the brochure's range", () => {
    expect(typeHint(types[1], "round", 40).tone).toBe("warn")
    expect(typeHint(types[1], "round", 40).text).toContain("33–34 mm")
  })

  it("says nothing for a type of another shape", () => {
    expect(typeHint(types[1], "oval", null)).toBeNull()
  })
})

describe("initialState", () => {
  it("defaults to found, cleaned, fine and asks what was inside", () => {
    const state = fresh()
    expect(state).toMatchObject({
      found: "found",
      cleaning: "cleaned",
      contents: null,
      box_left: "fine",
      changes_open: false,
      date: "2026-11-03",
    })
    expect(state.id).toMatch(/^[0-9a-f-]{36}$/)
  })

  it("has no cleaning default for a box that isn't cleaned", () => {
    expect(fresh({}, { ...box, type_id: 11 }).cleaning).toBe("")
  })

  it("hangs a planned box", () => {
    expect(fresh({}, planned)).toMatchObject({
      hung: true,
      changes_open: true,
      cleaning: "",
    })
  })

  it("reads back an existing check", () => {
    const initial = {
      id: "check-1",
      date: "2026-10-24",
      made_at: "2026-10-24T10:00:00Z",
      found: "found",
      cleaning: "cleaned",
      not_cleaned_reason_id: null,
      contents: ["bird_nest"],
      occupant_ids: [1],
      eggs_left: true,
      dead_birds: false,
      breeding_note: "",
      box_left: "needs_repair",
      box_changes: { hole_size: 36 },
      note: "",
      photos: [],
    }
    expect(initialState(box, initial, types)).toMatchObject({
      id: "check-1",
      contents: "occupied",
      breeding: ["eggs_left"],
      box_left: "needs_repair",
      changes_open: true,
      verify: false,
      changes: { hole_size: 36, type: 2 },
    })
  })
})

describe("buildPayload", () => {
  it("builds an empty box's check", () => {
    const payload = buildPayload(fresh({ contents: "nothing" }), box, categories)
    expect(payload).toMatchObject({
      box_id: "box-1",
      date: "2026-11-03",
      found: "found",
      cleaning: "cleaned",
      contents: ["nothing"],
      occupant_ids: [],
      eggs_left: null,
      box_left: "fine",
      box_changes: {},
    })
    expect(Date.parse(payload.made_at)).not.toBeNaN()
  })

  it("derives the contents from the occupants", () => {
    const birds = buildPayload(
      fresh({ contents: "occupied", occupant_ids: [1], breeding: ["dead_birds"] }),
      box,
      categories,
    )
    expect(birds).toMatchObject({
      contents: ["bird_nest"],
      occupant_ids: [1],
      eggs_left: false,
      dead_birds: true,
    })
    const unknown = buildPayload(
      fresh({ contents: "occupied", occupant_ids: [18, 27] }),
      box,
      categories,
    )
    expect(unknown).toMatchObject({ contents: ["other_animal"], eggs_left: null })
  })

  it("asks nothing more of a box not found", () => {
    const payload = buildPayload(
      fresh({ found: "not_found", contents: "nothing", changes_open: true }),
      box,
      categories,
    )
    expect(payload).toMatchObject({
      found: "not_found",
      cleaning: "",
      contents: [],
      box_left: "",
      box_changes: {},
    })
  })

  it("can't see inside a box that wouldn't open", () => {
    const payload = buildPayload(fresh({ cleaning: "could_not_open" }), box, categories)
    expect(payload.contents).toEqual(["unknown"])
  })

  it("sends only what changed on the box", () => {
    const state = fresh({ contents: "nothing", changes_open: true })
    state.changes = { ...state.changes, hole_size: 36 }
    expect(buildPayload(state, box, categories).box_changes).toEqual({ hole_size: 36 })
  })

  it("sends every verification field to verify a box", () => {
    const unverified = { ...box, is_verified: false }
    const state = fresh(
      { contents: "nothing", changes_open: true, verify: true },
      unverified,
    )
    expect(
      Object.keys(buildPayload(state, unverified, categories).box_changes),
    ).toEqual(expect.arrayContaining(VERIFICATION_FIELDS))
  })

  it("hangs a planned box where the phone says", () => {
    const state = fresh({}, planned)
    const hungAt = { type: "Point", coordinates: [14.3631, 50.0701] }
    state.changes = { ...state.changes, location: hungAt }
    expect(buildPayload(state, planned, categories)).toMatchObject({
      found: "found",
      cleaning: "",
      contents: [],
      box_changes: { hung: true, location: hungAt },
    })
  })
})

describe("validate", () => {
  it("wants to know what was inside", () => {
    expect(validate(fresh(), box)).toHaveProperty("contents")
    expect(validate(fresh({ contents: "nothing" }), box)).toEqual({})
  })

  it("wants the occupants of an occupied box", () => {
    expect(validate(fresh({ contents: "occupied" }), box)).toHaveProperty(
      "occupant_ids",
    )
  })

  it("wants the reason a box wasn't cleaned", () => {
    expect(
      validate(fresh({ contents: "nothing", cleaning: "not_cleaned" }), box),
    ).toHaveProperty("not_cleaned_reason_id")
  })

  it("asks nothing of a box not found", () => {
    expect(validate(fresh({ found: "not_found" }), box)).toEqual({})
  })

  it("wants every verification field", () => {
    const state = fresh({ contents: "nothing", changes_open: true, verify: true })
    state.changes = { ...state.changes, opening: "" }
    expect(validate(state, box)).toEqual({ opening: "Vyber, jak se budka otevírá." })
  })
})
