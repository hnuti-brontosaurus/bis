const numberFormat = new Intl.NumberFormat("cs-CZ")

export const formatNumber = value => numberFormat.format(value)

export const plural = (count, one, few, many) => {
  if (count === 1) return one
  if (count >= 2 && count <= 4) return few
  return many
}

export const percent = (part, whole) =>
  whole ? `${Math.round((part / whole) * 100)} %` : "–"

export const pendingLabel = count =>
  `${count} ${plural(count, "čeká", "čekají", "čeká")}`

export const areaCountLabel = count =>
  `${count} ${plural(count, "oblast", "oblasti", "oblastí")}`

export const boxCountLabel = count =>
  `${formatNumber(count)} ${plural(count, "budka", "budky", "budek")}`

export const seasonLabel = season => `${season}/${String(season + 1).slice(-2)}`

export const currentSeason = (today = new Date()) =>
  today.getMonth() >= 6 ? today.getFullYear() : today.getFullYear() - 1

const dateFormat = new Intl.DateTimeFormat("cs-CZ")

/** "2026-11-03" or an ISO datetime → "3. 11. 2026" */
export const formatDate = value => (value ? dateFormat.format(new Date(value)) : "–")

/** Today in the phone's own time zone, as the API's ISO date. */
export const isoDate = (day = new Date()) => day.toLocaleDateString("sv-SE")

export const seasonOf = isoDay => currentSeason(new Date(isoDay))

export const seasonStart = season => `${season}-07-01`

export const daysBetween = (from, to = new Date()) =>
  Math.floor((to - new Date(from)) / 86_400_000)

export const dayCountLabel = count => `${count} ${plural(count, "den", "dny", "dní")}`

export const checkCountLabel = count =>
  `${count} ${plural(count, "kontrola", "kontroly", "kontrol")}`

export const formatDistance = metres =>
  metres === null || metres === undefined ? "–" : `${Math.round(metres)} m`
