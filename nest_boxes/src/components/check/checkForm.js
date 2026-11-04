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

const CONTENT_CHOICES = ["bird_nest", "other_animal", "nothing", "unknown"]

const contentsChoice = contents =>
  CONTENT_CHOICES.find(choice => contents?.includes(choice)) ?? null

const defaultCleaning = (box, types) =>
  types.find(type => type.id === box.type_id)?.needs_cleaning === false ? "" : "cleaned"

/** The box's required data it lacks, which a check asks for as if to verify it. */
export const missingBoxFields = box => {
  const values = boxValues(box)
  return VERIFICATION_FIELDS.filter(key =>
    key === "hole_size"
      ? MEASURED_HOLE_SHAPES.includes(box.hole_shape) && !box.hole_size
      : !values[key],
  )
}

/** The form's state for a new check of `box`, or for editing `initial`. */
export const initialState = (box, initial, types, date = isoDate()) => {
  // A check that hangs a box asks nothing about cleaning, see validate_check
  const hanging = box.status === "planned" || Boolean(initial?.box_changes?.hung)
  const verify = !box.is_verified || missingBoxFields(box).length > 0
  const changes = { ...boxValues(box), ...(initial?.box_changes ?? {}) }
  delete changes.hung
  if (!initial)
    return {
      id: uuid(),
      date,
      made_at: null,
      found: "found",
      hanging,
      hung: hanging,
      cleaning: hanging ? "" : defaultCleaning(box, types),
      not_cleaned_reason_id: null,
      contents: null,
      occupant_ids: [],
      breeding: [],
      breeding_note: "",
      box_left: "fine",
      changes_open: verify,
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
    hanging,
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
    changes_open: verify || changedKeys.length > 0,
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

const reasonOf = (state, reasons) =>
  reasons.find(reason => reason.id === state.not_cleaned_reason_id)

/** Picks why the box wasn't cleaned; a reason that tells who is inside says so. */
export const chooseReason = (state, reasonId, { not_cleaned_reasons, occupants }) => {
  state.not_cleaned_reason_id = reasonId
  const reason = not_cleaned_reasons.find(item => item.id === reasonId)
  const occupant = occupants.find(item => item.id === reason?.occupant_id)
  if (!occupant) return
  state.contents = occupant.is_bird ? "bird_nest" : "other_animal"
  state.occupant_ids = [occupant.id]
}

/**
 * Whether the form asks what was inside: of a found box that isn't hung now,
 * unless it wasn't cleaned for a reason that leaves the inside unknown.
 */
export const asksContents = (state, { not_cleaned_reasons }) =>
  state.found === "found" &&
  !state.hanging &&
  (state.cleaning !== "not_cleaned" ||
    Boolean(reasonOf(state, not_cleaned_reasons)?.contents_known))

/** The chosen occupants of the kind the contents say: birds for a nest. */
export const chosenOccupants = (state, occupants) =>
  occupants
    .filter(occupant => state.occupant_ids.includes(occupant.id))
    .filter(occupant =>
      state.contents === "bird_nest" ? occupant.is_bird : !occupant.is_bird,
    )

const OCCUPIED = ["bird_nest", "other_animal"]

/** The check exactly as the API takes it. */
export const buildPayload = (state, box, categories) => {
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
  if (state.found !== "found" || state.hanging) return payload
  payload.cleaning = state.cleaning
  payload.box_left = state.box_left
  if (state.cleaning === "not_cleaned")
    payload.not_cleaned_reason_id = state.not_cleaned_reason_id
  if (!asksContents(state, categories)) return payload
  payload.contents = [state.contents]
  if (OCCUPIED.includes(state.contents))
    payload.occupant_ids = chosenOccupants(state, categories.occupants).map(
      occupant => occupant.id,
    )
  if (state.contents === "bird_nest") {
    payload.eggs_left = state.breeding.includes("eggs_left")
    payload.dead_birds = state.breeding.includes("dead_birds")
    payload.breeding_note = state.breeding_note
  }
  return payload
}

const OCCUPANT_ERRORS = {
  bird_nest: "Vyber, který pták tu hnízdil. Když nevíš, vyber „pták (nevím jaký)“.",
  other_animal: "Vyber, jaké zvíře tu bylo. Když nevíš, vyber „nevím“.",
}

/** Messages per field; empty when the check can be saved. Mirrors validate_check. */
export const validate = (state, categories, initial = null) => {
  const errors = {}
  if (!state.date) errors.date = "Zadej datum kontroly."
  if (state.found !== "found") {
    if (!state.note.trim()) errors.note = "Napiš proč, správci to pomůže."
    return errors
  }
  if (state.hanging) {
    if (!state.changes.location) errors.location = "Zadej, kde budka visí."
  } else {
    if (state.cleaning === "not_cleaned" && !state.not_cleaned_reason_id)
      errors.not_cleaned_reason_id = "Vyber, proč se nevyčistila."
    if (asksContents(state, categories)) {
      if (!state.contents) errors.contents = "Vyber, co bylo uvnitř."
      else if (
        OCCUPIED.includes(state.contents) &&
        !chosenOccupants(state, categories.occupants).length &&
        // An imported check may say what was inside without saying who
        !initial?.contents.includes(state.contents)
      )
        errors.occupant_ids = OCCUPANT_ERRORS[state.contents]
    }
  }
  if (state.changes_open && state.verify) {
    const { changes } = state
    if (!changes.name) errors.name = "Bez označení budku neověříš."
    if (!changes.location) errors.location ??= "Bez polohy budku neověříš."
    if (!changes.hole_shape) errors.hole_shape = "Vyber tvar otvoru."
    if (MEASURED_HOLE_SHAPES.includes(changes.hole_shape) && !changes.hole_size)
      errors.hole_size = "Změř šířku otvoru."
    if (!changes.type) errors.type = "Vyber typ budky."
    if (!changes.opening) errors.opening = "Vyber, jak se budka otevírá."
  }
  return errors
}
