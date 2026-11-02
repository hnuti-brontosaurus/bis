import {
  formatYearRanges,
  groupMemberships,
} from 'user/pages/ViewProfile/groupMemberships'

const YOUNG = { id: 1, name: 'individuální 15-26 let', slug: 'young' }
const ADULT = { id: 2, name: 'individuální nad 26 let', slug: 'adult' }

describe('groupMemberships', () => {
  it('merges years of one unit and type, newest group first', () => {
    const groups = groupMemberships([
      { administration_unit: 7, category: YOUNG, year: 2020 },
      { administration_unit: 7, category: ADULT, year: 2023 },
      { administration_unit: 7, category: YOUNG, year: 2021 },
      { administration_unit: 7, category: ADULT, year: 2022 },
    ])

    expect(groups.map(({ category, years }) => [category.id, years])).toEqual([
      [ADULT.id, [2022, 2023]],
      [YOUNG.id, [2020, 2021]],
    ])
  })

  it('keeps units apart and drops duplicate years', () => {
    const groups = groupMemberships([
      { administration_unit: 7, category: YOUNG, year: 2020 },
      { administration_unit: 7, category: YOUNG, year: 2020 },
      { administration_unit: 8, category: YOUNG, year: 2019 },
    ])

    expect(
      groups.map(({ administration_unit, years }) => [
        administration_unit,
        years,
      ]),
    ).toEqual([
      [7, [2020]],
      [8, [2019]],
    ])
  })
})

describe('formatYearRanges', () => {
  it.each([
    [[2025], '2025'],
    [[2014, 2015, 2016], '2014–2016'],
    [[2014, 2015, 2018, 2020, 2021], '2014–2015, 2018, 2020–2021'],
  ])('formats %j as %s', (years, expected) => {
    expect(formatYearRanges(years)).toBe(expected)
  })
})
