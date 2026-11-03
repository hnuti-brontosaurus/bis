import { User } from 'app/services/bisTypes'
import { groupBy, sortBy, uniq } from 'lodash'

export const groupMemberships = (memberships: User['memberships']) => {
  const groups = Object.entries(
    groupBy(
      memberships,
      membership =>
        `${membership.administration_unit}-${membership.category.id}`,
    ),
  ).map(([key, group]) => ({
    key,
    administration_unit: group[0].administration_unit,
    category: group[0].category,
    years: sortBy(uniq(group.map(({ year }) => year))),
  }))

  return sortBy(groups, ({ years }) => -years[years.length - 1])
}

export const formatYearRanges = (uniqueSortedYears: number[]) => {
  const ranges: [number, number][] = []
  for (const year of uniqueSortedYears) {
    const lastRange = ranges[ranges.length - 1]
    if (lastRange?.[1] === year - 1) lastRange[1] = year
    else ranges.push([year, year])
  }
  return ranges
    .map(([first, last]) => (first === last ? `${first}` : `${first}–${last}`))
    .join(', ')
}
