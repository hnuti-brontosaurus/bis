// Set by the escape button of the old BIS, see
// backend/old_bis/static/old_bis/escape.js
const ESCAPED_KEY = 'old-bis-escaped'

export const redirectToOldBisOnAprilFools = () => {
  const [year, month, day] = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Europe/Prague',
  })
    .format(new Date())
    .split('-')
  if (
    month === '04' &&
    day === '01' &&
    window.location.pathname === '/' &&
    localStorage.getItem(ESCAPED_KEY) !== year
  ) {
    window.location.replace('/stary/')
  }
}
