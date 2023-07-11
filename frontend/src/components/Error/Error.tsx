import type { SerializedError } from '@reduxjs/toolkit'
import type { FetchBaseQueryError } from '@reduxjs/toolkit/query'
import { useTitle } from 'hooks/title'
import { ReactNode } from 'react'
import styles from './Error.module.scss'

export const Error = ({
  error,
  children,
  message,
  status,
}: {
  children?: ReactNode
  error?: FetchBaseQueryError | SerializedError
  message?: string
  status?: number | string
}) => {
  let name = 'Něco se pokazilo...'

  if (message) {
    name = message
  } else if (error && 'status' in error) {
    switch (error.status) {
      case 404:
        status = 404
        name = 'Objekt nenalezen'
        break
      case 500:
        status = 500
        name = 'Chyba serveru'
        break
      case 'FETCH_ERROR':
        status = 500
        name = `Chyba při stahování dat (${error.error})`
        break
      case 'PARSING_ERROR':
        status = 500
        name = `Chyba při zpracování dat (${error.error})`
        break
      default:
        break
      case 'CUSTOM_ERROR':
        status = error.status
        name = error.error
    }
  } else {
    status = error?.code ?? status
    name = error?.message ?? name
  }

  useTitle('Něco se pokazilo')

  return (
    <div className={styles.container}>
      {status && <div className={styles.status}>{status}</div>}
      <div className={styles.message}>{name}</div>
      {children}
    </div>
  )
}
