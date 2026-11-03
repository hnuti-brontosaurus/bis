import { checkResult, lastCheckedLabel, typeName } from "@/composables/boxes.js"
import { seasonStart } from "@/composables/czech.js"
import { CONDITION_LABELS, STATUS_LABELS } from "@/composables/labels.js"
import { compareNames } from "@/composables/linkBoxes.js"

// Ended and cancelled boxes are history; the list starts without them.
export const ACTIVE_STATUSES = ["planned", "in_use", "taken_down", "missing"]

export const CHECKED_OPTIONS = [
  { value: "this_season", label: "Letos zkontrolované" },
  { value: "before", label: "Naposledy před letoškem" },
  { value: "never", label: "Nikdy zkontrolované" },
]

export const defaultFilters = () => ({
  status: [...ACTIVE_STATUSES],
  state: [],
  type: [],
  unverified: false,
  checked: null,
  search: "",
})

const normalized = text => text.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()

/** The client side of the boxes/ filters, so the list and the exports agree. */
export const filterBoxes = (boxes, filters, season) => {
  const start = seasonStart(season)
  const search = normalized(filters.search.trim())
  return boxes.filter(
    box =>
      (!filters.status.length || filters.status.includes(box.status)) &&
      (!filters.state.length || filters.state.includes(box.season_state)) &&
      (!filters.type.length || filters.type.includes(box.type_id)) &&
      (!filters.unverified || !box.is_verified) &&
      (filters.checked !== "this_season" ||
        (box.last_checked_on && box.last_checked_on >= start)) &&
      (filters.checked !== "before" ||
        (box.last_checked_on && box.last_checked_on < start)) &&
      (filters.checked !== "never" || !box.last_checked_on) &&
      (!search || normalized(`${box.name} ${box.previous_names}`).includes(search)),
  )
}

/** The same filters as query parameters of export.gpx / export.xlsx. */
export const filterParams = (filters, season) => {
  const start = seasonStart(season)
  return {
    status: filters.status,
    season_state: filters.state,
    type: filters.type,
    ...(filters.unverified && { is_verified: false }),
    ...(filters.checked === "this_season" && { last_checked_after: start }),
    ...(filters.checked === "before" && { last_checked_before: start }),
    ...(filters.checked === "never" && { never_checked: true }),
  }
}

/** Boxes in the batch first, the rest after; both by name. */
export const splitByBatch = (boxes, batch) => {
  const inBatch = new Set(batch?.box_ids ?? [])
  return {
    inBatch: boxes.filter(box => inBatch.has(box.id)).sort(compareNames),
    outside: boxes.filter(box => !inBatch.has(box.id)).sort(compareNames),
  }
}

/** The state a box's marker shows, see map/markers.js; an ended box has none. */
export const markerState = (box, batch) =>
  (!batch || batch.box_ids.includes(box.id)) && box.season_state
    ? box.season_state
    : "out"

/**
 * The second line of a box row: its type and what the season's check found,
 * or why a box outside the batch may not need one.
 */
export const boxRowDetail = (
  box,
  check,
  { typesById, occupantsById, otherBatches },
) => {
  const type = typeName(typesById, box.type_id)
  if (box.status === "planned") return { text: `plánovaná · ${type}` }
  if (check)
    return {
      text: `${type} · ${checkResult(check, occupantsById)}${check.is_confirmed ? "" : " · čeká"}`,
    }
  if (box.status !== "in_use")
    return { text: `${type} · ${STATUS_LABELS[box.status]}`, tone: "warn" }
  if (typesById.get(box.type_id)?.needs_cleaning === false)
    return { text: `${type} · nečistí se`, tone: "info" }
  if (box.condition !== "fine")
    return { text: `${type} · ${CONDITION_LABELS[box.condition]}`, tone: "bad" }
  if (box.should_be_moved) return { text: `${type} · přemístit`, tone: "warn" }
  const other = otherBatches.find(batch => batch.box_ids.includes(box.id))
  if (other) return { text: `${type} · v dávce ${other.name}` }
  if (!box.is_verified) return { text: `${type} · neověřená`, tone: "warn" }
  return { text: `${type} · ${lastCheckedLabel(box)}` }
}
