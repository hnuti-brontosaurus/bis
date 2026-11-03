import { VERIFICATION_FIELDS } from "@/components/check/checkForm.js"
import { distance } from "@/components/map/geometry.js"
import { formatDate } from "@/composables/czech.js"
import {
  BOX_LEFT_LABELS,
  CLEANING_LABELS,
  CONDITION_LABELS,
  FOUND_LABELS,
  HOLE_SHAPE_LABELS,
  MATERIAL_LABELS,
  MEASURED_HOLE_SHAPES,
  OPENING_LABELS,
  STATUS_LABELS,
} from "@/composables/labels.js"

export const mapyLink = location =>
  `https://mapy.com/fnc/v1/showmap?mapset=outdoor&center=${location.coordinates[0]},${location.coordinates[1]}&zoom=18&marker=true`

export const holeLabel = box => {
  if (!box.hole_shape) return ""
  const shape = HOLE_SHAPE_LABELS[box.hole_shape]
  return MEASURED_HOLE_SHAPES.includes(box.hole_shape) && box.hole_size
    ? `${shape} · ${box.hole_size} mm`
    : shape
}

export const typeName = (typesById, typeId) =>
  typesById.get(typeId)?.name ?? "typ neznámý"

/** "velký sýkorník · kulatý · 33 mm · přední" */
export const boxSummary = (box, typesById) =>
  [typeName(typesById, box.type_id), holeLabel(box), OPENING_LABELS[box.opening]]
    .filter(Boolean)
    .join(" · ")

/** One line saying what a check found: "vyčištěno · sýkora koňadra · potřebuje opravu" */
export const checkResult = (check, occupantsById) => {
  if (check.found !== "found") return FOUND_LABELS[check.found]
  if (check.box_changes?.hung) return "pověšena"
  const occupants = check.occupant_ids.map(id => occupantsById.get(id)?.name)
  const contents = check.contents.includes("nothing")
    ? ["prázdná"]
    : occupants.length
      ? occupants
      : check.contents.includes("unknown")
        ? ["obsah nevím"]
        : check.contents.length
          ? ["obsazená"]
          : []
  return [
    CLEANING_LABELS[check.cleaning],
    ...contents,
    check.box_left && check.box_left !== "fine" ? BOX_LEFT_LABELS[check.box_left] : "",
  ]
    .filter(Boolean)
    .join(" · ")
}

/** The marker state of a box given its check this season, see map/markers.js. */
export const checkState = check => {
  if (!check || check.found === "not_reached") return "todo"
  return check.found === "not_found" ? "not_found" : "done"
}

export const lastCheckedLabel = box =>
  box.last_checked_on
    ? `kontrola ${formatDate(box.last_checked_on)}`
    : "nikdy kontrolovaná"

const FIELD_LABELS = {
  name: "označení",
  previous_names: "dřívější označení",
  status: "stav",
  condition: "stav budky",
  location: "poloha",
  planned_radius: "okruh",
  area: "oblast",
  type: "typ",
  hole_shape: "tvar otvoru",
  hole_size: "otvor",
  opening: "otevírání",
  material: "materiál",
  predator_guard: "ochrana proti predátorům",
  access_note: "přístup",
  owner_note: "poznámka k majiteli",
  note: "poznámka",
  installed_on: "vyvěšena",
  ended_on: "ukončena",
  end_reason: "důvod ukončení",
  is_verified: "ověřená",
  is_confirmed: "potvrzená",
  elevation: "nadmořská výška",
}

const CHOICE_LABELS = {
  status: STATUS_LABELS,
  condition: CONDITION_LABELS,
  hole_shape: HOLE_SHAPE_LABELS,
  opening: OPENING_LABELS,
  material: MATERIAL_LABELS,
}

const point = coordinates => ({ type: "Point", coordinates })

const isEmpty = value => value === null || value === "" || value === undefined

/** A NestBoxHistory entry as Czech text; the one that created the box says just that. */
export const describeHistory = (changes, context) =>
  Object.values(changes).every(([before]) => isEmpty(before))
    ? "budka založena"
    : Object.entries(changes)
        .map(([field, values]) => describeChange(field, values, context))
        .join(", ")

/** One NestBoxHistory change as Czech text: "otvor 30 → 33". */
export const describeChange = (
  field,
  [before, after],
  { typesById, endReasonsById },
) => {
  const label = FIELD_LABELS[field] ?? field
  if (field === "location")
    return before && after
      ? `poloha posunuta o ${Math.round(distance(point(before), point(after)))} m`
      : "poloha zadána"
  const show = value => {
    if (isEmpty(value)) return "–"
    if (typeof value === "boolean") return value ? "ano" : "ne"
    if (field === "type") return typesById.get(value)?.name ?? value
    if (field === "end_reason") return endReasonsById.get(value)?.name ?? value
    if (field.endsWith("_on")) return formatDate(value)
    return CHOICE_LABELS[field]?.[value] ?? value
  }
  return `${label} ${show(before)} → ${show(after)}`
}

export const isVerification = changes =>
  VERIFICATION_FIELDS.every(field => field in changes)

/** A check's box_changes in short: "ověření" or "otvor 33 mm, typ velký sýkorník". */
export const boxChangesLabel = (changes, typesById) => {
  if (changes.hung) return "pověšena"
  if (isVerification(changes)) return "ověření údajů"
  return Object.entries(changes)
    .map(([field, value]) => {
      if (field === "location") return "poloha"
      if (field === "type") return `typ ${typesById.get(value)?.name ?? "–"}`
      if (field === "hole_size") return `otvor ${value ?? "–"} mm`
      if (field === "installed_on") return `vyvěšena ${formatDate(value)}`
      return `${FIELD_LABELS[field]} ${CHOICE_LABELS[field]?.[value] ?? value}`
    })
    .join(", ")
}
