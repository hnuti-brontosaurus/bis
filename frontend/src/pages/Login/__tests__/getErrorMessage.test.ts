import { getErrorMessage } from 'pages/Login/getErrorMessage'

describe('getErrorMessage', () => {
  it('returns auth error message for 400', () => {
    expect(getErrorMessage({ status: 400, data: null })).toBe(
      'Problém s vaším přihlášením, zadejte prosím správné uživatelské jméno a heslo.',
    )
  })

  it('returns auth error message for 401', () => {
    expect(getErrorMessage({ status: 401, data: null })).toBe(
      'Problém s vaším přihlášením, zadejte prosím správné uživatelské jméno a heslo.',
    )
  })

  it('returns server error message for 500', () => {
    expect(getErrorMessage({ status: 500, data: null })).toBe(
      'Byl problém s přihlášením. Prosím zkuste to znovu.',
    )
  })

  it('returns rate limit message for 429', () => {
    expect(getErrorMessage({ status: 429, data: null })).toBe(
      'Příliš mnoho neúspěšných pokusů o přihlášení k vašemu účtu. Před opětovným přihlášením musíte počkat 1 hodinu.',
    )
  })

  it('returns generic message for other errors', () => {
    expect(getErrorMessage({ status: 403, data: null })).toBe(
      'Nepodařilo se přihlásit',
    )
  })

  it('returns generic message for SerializedError', () => {
    expect(getErrorMessage({ name: 'Error', message: 'Network error' })).toBe(
      'Nepodařilo se přihlásit',
    )
  })
})
