import { percent } from "@/composables/czech.js"

export const ratio = (part, whole) => (whole ? part / whole : null)

export const describeFigures = figures => ({
  coverage: ratio(figures.cleaned, figures.boxes),
  coverageLabel: percent(figures.cleaned, figures.boxes),
  occupancyLabel: percent(figures.occupied, figures.inspected),
  birdOccupancyLabel: percent(figures.bird_occupied, figures.inspected),
  previousOccupancyLabel: percent(
    figures.previous_occupied,
    figures.previous_inspected,
  ),
})

export const unitsOf = areas =>
  [
    ...new Map(
      areas.map(area => [area.administration_unit.id, area.administration_unit]),
    ).values(),
  ].sort((a, b) => a.name.localeCompare(b.name, "cs"))

const withMarkers = (items, areas) => {
  const byId = new Map(areas.map(area => [area.id, area]))
  return items
    .map(item => ({ ...item, area: byId.get(item.area.id) }))
    .filter(item => item.area?.marker && item.count)
}

/** AreaBubbles' items from public/statistics/ rows: the season's boxes and their pie. */
export const statisticsBubbles = (rows, areas) =>
  withMarkers(
    rows.map(row => ({
      area: row.area,
      count: row.boxes,
      done: row.done,
      attention: row.attention,
    })),
    areas,
  )

/** AreaBubbles' items from areas/season_states/ rows, with the planned boxes too. */
export const stateBubbles = (rows, areas) =>
  withMarkers(
    rows.map(row => ({
      area: { id: row.area_id },
      count: row.planned + row.to_check + row.attention + row.done,
      done: row.done,
      attention: row.attention,
    })),
    areas,
  )
