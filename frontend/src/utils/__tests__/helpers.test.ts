import {
  checkVipPropagationFilled,
  getEventCannotBeOlderThan,
  getIdBySlug,
  getIdsBySlugs,
  isEventPast,
  joinDateTime,
  normalizeString,
  shouldBeFinishedUntil,
  splitDateTime,
  validateUrl,
} from '../helpers'

describe('validateUrl', () => {
  it('returns true for valid URLs', () => {
    expect(validateUrl('https://example.com')).toBe(true)
    expect(validateUrl('http://example.com/path?q=1')).toBe(true)
    expect(validateUrl('https://brontosaurus.cz/akce')).toBe(true)
  })

  it('returns error message for invalid URLs', () => {
    expect(validateUrl('not-a-url')).toBe(
      'Zadejte platný odkaz začínající https://',
    )
    expect(validateUrl('hello')).toBe(
      'Zadejte platný odkaz začínající https://',
    )
  })

  it('returns true for empty/undefined (optional field)', () => {
    expect(validateUrl('')).toBe(true)
    expect(validateUrl(undefined)).toBe(true)
  })
})

describe('splitDateTime', () => {
  it('splits datetime into date and time', () => {
    expect(splitDateTime('2023-01-15T14:30')).toEqual(['2023-01-15', '14:30'])
  })

  it('handles midnight', () => {
    expect(splitDateTime('2023-06-01T00:00')).toEqual(['2023-06-01', '00:00'])
  })
})

describe('joinDateTime', () => {
  it('joins date and time', () => {
    expect(joinDateTime('2023-01-15', '14:30')).toBe('2023-01-15T14:30')
  })

  it('defaults to 00:00 when time is empty', () => {
    expect(joinDateTime('2023-01-15', '')).toBe('2023-01-15T00:00')
    expect(joinDateTime('2023-01-15')).toBe('2023-01-15T00:00')
  })

  it('handles partial time input by zeroing invalid parts', () => {
    // '14' splits into hours='14', minutes=undefined → hours passes /^\d\d$/, minutes doesn't
    expect(joinDateTime('2023-01-15', '14')).toBe('2023-01-15T14:00')
  })
})

describe('checkVipPropagationFilled', () => {
  it('returns true when all three fields are filled', () => {
    expect(
      checkVipPropagationFilled({
        goals_of_event: 'goals',
        program: 'program',
        short_invitation_text: 'invitation',
      }),
    ).toBe(true)
  })

  it('returns false when any field is empty string', () => {
    expect(
      checkVipPropagationFilled({
        goals_of_event: 'goals',
        program: '',
        short_invitation_text: 'invitation',
      }),
    ).toBe(false)
  })

  it('returns false when any field is whitespace only', () => {
    expect(
      checkVipPropagationFilled({
        goals_of_event: 'goals',
        program: '   ',
        short_invitation_text: 'invitation',
      }),
    ).toBe(false)
  })

  it('returns false for null/undefined', () => {
    expect(checkVipPropagationFilled(null)).toBe(false)
    expect(checkVipPropagationFilled(undefined)).toBe(false)
  })

  it('returns false when fields are missing', () => {
    expect(checkVipPropagationFilled({})).toBe(false)
    expect(
      checkVipPropagationFilled({ goals_of_event: 'goals' }),
    ).toBe(false)
  })
})

describe('isEventPast', () => {
  it('returns true when event ended yesterday', () => {
    const now = new Date('2123-03-09T12:00:00')
    expect(isEventPast('2123-03-08', now)).toBe(true)
  })

  it('returns false when event ends today', () => {
    const now = new Date('2123-03-08T15:00:00')
    expect(isEventPast('2123-03-08', now)).toBe(false)
  })

  it('returns false when event ends in the future', () => {
    const now = new Date('2123-03-07T12:00:00')
    expect(isEventPast('2123-03-08', now)).toBe(false)
  })

  it('handles midnight boundary correctly', () => {
    const now = new Date('2123-03-09T00:00:00')
    expect(isEventPast('2123-03-08', now)).toBe(true)
  })
})

describe('getEventCannotBeOlderThan', () => {
  const RealDate = Date

  afterEach(() => {
    global.Date = RealDate
  })

  const mockDate = (dateString: string) => {
    const fixed = new RealDate(dateString)
    global.Date = class extends RealDate {
      constructor(...args: any[]) {
        if (args.length === 0) {
          super(fixed.getTime())
        } else {
          super(...(args as [any]))
        }
      }
    } as any
  }

  it('before March: allows events from previous year', () => {
    mockDate('2023-02-28')
    expect(getEventCannotBeOlderThan()).toBe('2022-01-01')
  })

  it('in March or later: only allows events from current year', () => {
    mockDate('2023-03-01')
    expect(getEventCannotBeOlderThan()).toBe('2023-01-01')
  })

  it('in January: allows events from previous year', () => {
    mockDate('2023-01-15')
    expect(getEventCannotBeOlderThan()).toBe('2022-01-01')
  })

  it('in December: only allows events from current year', () => {
    mockDate('2023-12-15')
    expect(getEventCannotBeOlderThan()).toBe('2023-01-01')
  })
})

describe('shouldBeFinishedUntil', () => {
  it('returns March 1 of the next year after event end', () => {
    const result = shouldBeFinishedUntil({ end: '2022-12-29' })
    const date = new Date(result)
    expect(date.getFullYear()).toBe(2023)
    expect(date.getMonth()).toBe(2) // March (0-indexed)
    expect(date.getDate()).toBe(1)
  })

  it('event ending in January still gets next year March deadline', () => {
    const result = shouldBeFinishedUntil({ end: '2023-01-15' })
    const date = new Date(result)
    expect(date.getFullYear()).toBe(2024)
    expect(date.getMonth()).toBe(2)
    expect(date.getDate()).toBe(1)
  })
})

describe('getIdBySlug', () => {
  const objects = [
    { id: 1, slug: 'alpha' },
    { id: 2, slug: 'beta' },
    { id: 3, slug: 'gamma' },
  ]

  it('returns id for matching slug', () => {
    expect(getIdBySlug(objects, 'beta')).toBe(2)
  })

  it('returns -1 for non-existent slug', () => {
    expect(getIdBySlug(objects, 'delta')).toBe(-1)
  })
})

describe('getIdsBySlugs', () => {
  const objects = [
    { id: 1, slug: 'alpha' },
    { id: 2, slug: 'beta' },
    { id: 3, slug: 'gamma' },
  ]

  it('returns ids for matching slugs', () => {
    expect(getIdsBySlugs(objects, ['alpha', 'gamma'])).toEqual([1, 3])
  })
})

describe('normalizeString', () => {
  it('lowercases and removes diacritics', () => {
    expect(normalizeString('Příliš')).toBe('prilis')
    expect(normalizeString('Žluťoučký')).toBe('zlutoucky')
  })

  it('handles plain ASCII', () => {
    expect(normalizeString('Hello World')).toBe('hello world')
  })
})
