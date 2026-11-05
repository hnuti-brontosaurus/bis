import { distance } from "@/components/map/geometry.js"
import { checkResult, lastCheckedLabel } from "@/composables/boxes.js"
import { compareNames } from "@/composables/linkBoxes.js"

// A box on a tree, or about to be; ended ones are history.
export const ACTIVE_STATUSES = [
  "planned",
  "in_use",
  "needs_repair",
  "needs_replacing",
  "taken_down",
  "missing",
]

// An ended box this close to a box that isn't ended was replaced by it
const REPLACED_WITHIN = 5

/**
 * `boxes` without the ended ones some box of `others` (not ended) hangs in
 * place of, which on a map would only cover their replacement.
 */
export const withoutReplaced = (boxes, others = boxes) => {
  const current = others.filter(box => box.status !== "ended")
  return boxes.filter(
    box =>
      box.status !== "ended" ||
      !current.some(other => distance(box.location, other.location) <= REPLACED_WITHIN),
  )
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
 * The lines an opened box row adds under its type: what the season's check
 * found, or why the box may need none, and when it was last checked.
 */
export const boxExtras = (box, check, { typesById, occupantsById, otherBatches }) => {
  if (["planned", "ended"].includes(box.status)) return []
  const lines = []
  if (check)
    lines.push(
      `Letos: ${checkResult(check, occupantsById)}${check.is_confirmed ? "" : " · čeká na potvrzení"}`,
    )
  else if (typesById.get(box.type_id)?.needs_cleaning === false)
    lines.push("Tento typ se nečistí.")
  const other = otherBatches.find(batch => batch.box_ids.includes(box.id))
  if (other) lines.push(`V obchůzce ${other.name}`)
  const last = lastCheckedLabel(box)
  lines.push(last.charAt(0).toUpperCase() + last.slice(1))
  return lines
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
