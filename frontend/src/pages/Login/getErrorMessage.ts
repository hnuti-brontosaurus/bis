import type { SerializedError } from '@reduxjs/toolkit'
import type { FetchBaseQueryError } from '@reduxjs/toolkit/query'

export const getErrorMessage = (
  error: FetchBaseQueryError | SerializedError,
): string => {
  if ('status' in error) {
    if (error.status === 400 || error.status === 401)
      return 'Problém s vaším přihlášením, zadejte prosím správné uživatelské jméno a heslo.'
    else if (error.status === 500) {
      return 'Byl problém s přihlášením. Prosím zkuste to znovu.'
    } else if (error.status === 429) {
      return 'Příliš mnoho neúspěšných pokusů o přihlášení k vašemu účtu. Před opětovným přihlášením musíte počkat 1 hodinu.'
    }
  }
  return 'Nepodařilo se přihlásit'
}
