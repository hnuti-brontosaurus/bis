import { checkResult, lastCheckedLabel, typeName } from "@/composables/boxes.js"
import { CONDITION_LABELS, STATUS_LABELS } from "@/composables/labels.js"
import { compareNames } from "@/composables/linkBoxes.js"

// A box on a tree, or about to be; ended ones are history.
export const ACTIVE_STATUSES = ["planned", "in_use", "taken_down", "missing"]

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
  if (other) return { text: `${type} · v obchůzce ${other.name}` }
  if (!box.is_verified) return { text: `${type} · neověřená`, tone: "warn" }
  return { text: `${type} · ${lastCheckedLabel(box)}` }
}

/** BoxList's groups of the map of all boxes: one per area, both by name. */
export const groupByArea = (boxes, areasById) => {
  const byArea = new Map()
  for (const box of boxes) {
    if (!byArea.has(box.area_id)) byArea.set(box.area_id, [])
    byArea.get(box.area_id).push(box)
  }
  return [...byArea]
    .map(([areaId, areaBoxes]) => ({
      key: areaId,
      title: areasById.get(areaId).name,
      boxes: areaBoxes.sort(compareNames),
    }))
    .sort((a, b) => a.title.localeCompare(b.title, "cs"))
}
