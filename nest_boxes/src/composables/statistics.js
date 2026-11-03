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

export const recentSeasons = (season, count) =>
  Array.from({ length: count }, (_, index) => season - index)
