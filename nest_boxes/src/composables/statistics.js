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
  ].sort((a, b) => a.abbreviation.localeCompare(b.abbreviation, "cs"))

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

const sumSeasons = rows =>
  rows[0].seasons.map((_, index) =>
    Object.fromEntries(
      Object.keys(rows[0].seasons[index]).map(figure => [
        figure,
        rows.reduce((total, row) => total + row.seasons[index][figure], 0),
      ]),
    ),
  )

/**
 * public/statistics/seasons/ rows grouped by administration unit, each group
 * and the whole table with its totals per season; raw counts, like the rows.
 */
export const seasonTable = rows => {
  const units = unitsOf(rows.map(row => row.area)).map(unit => {
    const areas = rows
      .filter(row => row.area.administration_unit.id === unit.id)
      .sort((a, b) => a.area.name.localeCompare(b.area.name, "cs"))
    return { unit, areas, seasons: sumSeasons(areas) }
  })
  return { units, total: rows.length ? sumSeasons(rows) : [] }
}
