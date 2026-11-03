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
