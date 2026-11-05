import { HANGING_STATUSES } from "@/composables/labels.js"
import { distance } from "@/components/map/geometry.js"

// The limits of `spacing_warnings` in backend/nest_boxes/boxes.py, from
// backend/nest_boxes/models.py: a volunteer offline gets the same warning.
const EXISTING_ANY_TYPE_LIMIT = 5
const EXISTING_SAME_TYPE_LIMIT = 15
const PLACING_ANY_TYPE_LIMIT = 15
const PLACING_SAME_TYPE_LIMIT = 50

const byName = new Intl.Collator("cs", { numeric: true })

export const compareNames = (a, b) => byName.compare(a.name, b.name)

/** Nearest first from `position` (a GeoJSON point), by name without one. */
export const sortBoxes = (boxes, position) =>
  [...boxes].sort((a, b) =>
    position
      ? distance(position, a.location) - distance(position, b.location) ||
        compareNames(a, b)
      : compareNames(a, b),
  )

/** One check per box: the season's check made later on a phone wins. */
export const latestChecks = checks => {
  const byBox = new Map()
  for (const check of checks) {
    const known = byBox.get(check.box_id)
    if (!known || check.made_at > known.made_at) byBox.set(check.box_id, check)
  }
  return byBox
}

export const isInUse = box => HANGING_STATUSES.includes(box.status)

/** Where a box is now: a hanging check moves a planned box to where it went up. */
export const boxLocation = (box, check) => check?.box_changes?.location ?? box.location

/** Mirrors `spacing_warnings`, over the boxes the link knows. */
export const spacingWarnings = (boxes, location, typeId, excludeId) =>
  boxes
    .filter(box => isInUse(box) && box.id !== excludeId)
    .map(box => ({
      box,
      distance: distance(location, box.location),
      isSameType: typeId !== null && box.type_id === typeId,
    }))
    .filter(
      ({ distance, isSameType }) =>
        distance < PLACING_SAME_TYPE_LIMIT &&
        (isSameType || distance < PLACING_ANY_TYPE_LIMIT),
    )
    .map(warning => ({
      ...warning,
      shouldBeMoved:
        warning.distance < EXISTING_ANY_TYPE_LIMIT ||
        (warning.isSameType && warning.distance < EXISTING_SAME_TYPE_LIMIT),
    }))
    .sort((a, b) => a.distance - b.distance)

export const SPACING_HINT =
  `Novou budku dávej aspoň ${PLACING_ANY_TYPE_LIMIT} m od jiných budek ` +
  `a ${PLACING_SAME_TYPE_LIMIT} m od budek stejného typu.`

/** Mirrors `duplicate_names`. */
export const duplicateNames = (boxes, name, excludeId) => {
  const wanted = name.trim().toLocaleLowerCase("cs")
  return wanted
    ? boxes.filter(
        box =>
          isInUse(box) &&
          box.id !== excludeId &&
          box.name.trim().toLocaleLowerCase("cs") === wanted,
      )
    : []
}
