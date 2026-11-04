import { isoDate } from "@/composables/czech.js"
import { MEASURED_HOLE_SHAPES } from "@/composables/labels.js"
import { uuid } from "@/composables/uuid.js"

// Keys of a check's `box_changes`, see nest_boxes/checks.py.
export const BOX_CHANGE_FIELDS = [
  "name",
  "hole_shape",
  "hole_size",
  "type",
  "opening",
  "material",
  "location",
  "installed_on",
]

// Any confirmed check verifies a box, so the check of an unverified one
// confirms all of these on the spot.
export const VERIFICATION_FIELDS = [
  "name",
  "location",
  "hole_shape",
  "hole_size",
  "type",
  "opening",
]

/** The box's own values under the `box_changes` keys. */
export const boxValues = box => ({
  name: box.name,
  hole_shape: box.hole_shape,
  hole_size: box.hole_size,
  type: box.type_id,
  opening: box.opening,
  material: box.material,
  location: box.location,
  installed_on: box.installed_on,
})

/** Mirrors `suggest_type` in nest_boxes/boxes.py. */
export const suggestType = (types, holeShape, holeSize) => {
  if (!holeShape) return null
  const sized = holeSize !== null && holeSize !== undefined && holeSize !== ""
  return (
    types.find(
      type =>
        type.hole_shape === holeShape &&
        (sized
          ? (type.hole_min === null || type.hole_min <= holeSize) &&
            (type.hole_max === null || type.hole_max >= holeSize)
          : type.hole_min === null && type.hole_max === null),
    ) ?? null
  )
}

const range = (min, max) =>
  min !== null && max !== null
    ? `${min}–${max} mm`
    : min !== null
      ? `od ${min} mm`
      : `do ${max} mm`

/**
 * What to say next to the type: that it follows from the hole, or that the
 * hole is outside the brochure's range for the type picked.
 */
export const typeHint = (type, holeShape, holeSize) => {
  if (!type || !holeShape || type.hole_shape !== holeShape) return null
  const sized = holeSize !== null && holeSize !== undefined && holeSize !== ""
  const { official_hole_min: min, official_hole_max: max } = type
  if (sized && (min !== null || max !== null)) {
    if ((min !== null && holeSize < min) || (max !== null && holeSize > max))
      return { tone: "warn", text: `podle brožury má mít otvor ${range(min, max)}` }
  }
  if (type.hole_min === null && type.hole_max === null) return null
  return { tone: "ok", text: `podle otvoru ${range(type.hole_min, type.hole_max)}` }
}

const CONTENT_CHOICES = { nothing: "nothing", unknown: "unknown" }

const contentsChoice = contents => {
  if (!contents?.length) return null
  if (contents.includes("bird_nest") || contents.includes("other_animal"))
    return "occupied"
  return CONTENT_CHOICES[contents[0]] ?? null
}

const defaultCleaning = (box, types) =>
  types.find(type => type.id === box.type_id)?.needs_cleaning === false ? "" : "cleaned"

/** The form's state for a new check of `box`, or for editing `initial`. */
export const initialState = (box, initial, types, date = isoDate()) => {
  const planned = box.status === "planned"
  const verify = !planned && !box.is_verified
  const changes = { ...boxValues(box), ...(initial?.box_changes ?? {}) }
  delete changes.hung
  if (!initial)
    return {
      id: uuid(),
      date,
      made_at: null,
      found: "found",
      hung: planned,
      cleaning: planned ? "" : defaultCleaning(box, types),
      not_cleaned_reason_id: null,
      contents: null,
      occupant_ids: [],
      breeding: [],
      breeding_note: "",
      box_left: "fine",
      changes_open: planned || verify,
      verify,
      changes,
      note: "",
    }
  const changedKeys = Object.keys(initial.box_changes ?? {}).filter(
    key => key !== "hung",
  )
  return {
    id: initial.id,
    date: initial.date,
    made_at: initial.made_at,
    found: initial.found,
    hung: Boolean(initial.box_changes?.hung),
    cleaning: initial.cleaning,
    not_cleaned_reason_id: initial.not_cleaned_reason_id,
    contents: contentsChoice(initial.contents),
    occupant_ids: [...initial.occupant_ids],
    breeding: [
      ...(initial.eggs_left ? ["eggs_left"] : []),
      ...(initial.dead_birds ? ["dead_birds"] : []),
    ],
    breeding_note: initial.breeding_note,
    box_left: initial.box_left || "fine",
    changes_open: planned || verify || changedKeys.length > 0,
    verify,
    changes,
    note: initial.note,
  }
}

const sameValue = (key, a, b) => {
  if (key === "location")
    return (
      Boolean(a) === Boolean(b) &&
      (!a ||
        a.coordinates.every(
          (coordinate, index) => Math.abs(coordinate - b.coordinates[index]) < 1e-7,
        ))
    )
  return (a ?? "") === (b ?? "")
}

/** What actually differs from the box, or everything to verify it. */
export const boxChanges = (state, box) => {
  if (state.found !== "found" || !state.changes_open) return {}
  const current = boxValues(box)
  const keys = BOX_CHANGE_FIELDS.filter(
    key =>
      !sameValue(key, state.changes[key], current[key]) ||
      (state.verify && VERIFICATION_FIELDS.includes(key)),
  )
  const changes = Object.fromEntries(keys.map(key => [key, state.changes[key]]))
  if (state.hung) return { ...changes, hung: true, location: state.changes.location }
  return changes
}

const isOccupied = state => state.contents === "occupied"

const occupiedContents = (state, occupants) => {
  const chosen = occupants.filter(occupant => state.occupant_ids.includes(occupant.id))
  return [
    ...(chosen.some(occupant => occupant.is_bird) ? ["bird_nest"] : []),
    ...(chosen.some(occupant => !occupant.is_bird) ? ["other_animal"] : []),
  ]
}

/** Whether the form asks what was inside: not for a box hung now, or one that would not open. */
export const asksContents = (state, box) =>
  state.found === "found" &&
  box.status !== "planned" &&
  state.cleaning !== "could_not_open"

const contentsOf = (state, occupants, initial) => {
  if (state.cleaning === "could_not_open") return ["unknown"]
  if (!isOccupied(state)) return [state.contents]
  const contents = occupiedContents(state, occupants)
  // An imported check may say "occupied" without saying by whom
  return contents.length ? contents : initial.contents
}

/** The check exactly as the API takes it. */
export const buildPayload = (state, box, { occupants }, initial = null) => {
  const found = state.found === "found"
  const planned = box.status === "planned"
  const payload = {
    id: state.id,
    box_id: box.id,
    date: state.date,
    made_at: state.made_at ?? new Date().toISOString(),
    found: state.found,
    cleaning: "",
    not_cleaned_reason_id: null,
    contents: [],
    occupant_ids: [],
    eggs_left: null,
    dead_birds: null,
    breeding_note: "",
    box_left: "",
    box_changes: boxChanges(state, box),
    note: state.note,
  }
  if (!found || planned) return payload
  payload.cleaning = state.cleaning
  if (state.cleaning === "not_cleaned")
    payload.not_cleaned_reason_id = state.not_cleaned_reason_id
  payload.contents = contentsOf(state, occupants, initial)
  if (isOccupied(state) && state.cleaning !== "could_not_open") {
    payload.occupant_ids = [...state.occupant_ids]
    if (payload.contents.includes("bird_nest")) {
      payload.eggs_left = state.breeding.includes("eggs_left")
      payload.dead_birds = state.breeding.includes("dead_birds")
      payload.breeding_note = state.breeding_note
    }
  }
  payload.box_left = state.box_left
  return payload
}

const hasInitialOccupants = initial =>
  ["bird_nest", "other_animal"].some(content => initial?.contents.includes(content))

/** Messages per field; empty when the check can be saved. */
export const validate = (state, box, initial = null) => {
  const errors = {}
  if (!state.date) errors.date = "Zadej datum kontroly."
  if (state.found !== "found") return errors
  if (box.status === "planned") {
    if (!state.changes.location) errors.location = "Zadej, kde budka visí."
  } else {
    if (state.cleaning === "not_cleaned" && !state.not_cleaned_reason_id)
      errors.not_cleaned_reason_id = "Vyber, proč se nevyčistila."
    if (asksContents(state, box)) {
      if (!state.contents) errors.contents = "Vyber, co bylo uvnitř."
      else if (
        isOccupied(state) &&
        !state.occupant_ids.length &&
        !hasInitialOccupants(initial)
      )
        errors.occupant_ids = "Vyber, kdo tam bydlel. Když nevíš, vyber „nevím“."
    }
  }
  if (state.changes_open && state.verify) {
    const { changes } = state
    if (!changes.name) errors.name = "Bez označení budku neověříš."
    if (!changes.location) errors.location = "Bez polohy budku neověříš."
    if (!changes.hole_shape) errors.hole_shape = "Vyber tvar otvoru."
    if (MEASURED_HOLE_SHAPES.includes(changes.hole_shape) && !changes.hole_size)
      errors.hole_size = "Změř šířku otvoru."
    if (!changes.type) errors.type = "Vyber typ budky."
    if (!changes.opening) errors.opening = "Vyber, jak se budka otevírá."
  }
  return errors
}
