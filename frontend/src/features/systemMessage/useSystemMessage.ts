import { SerializedError } from '@reduxjs/toolkit'
import { FetchBaseQueryError } from '@reduxjs/toolkit/dist/query'
import { useAppDispatch } from 'app/hooks'
import * as translations from 'config/static/combinedTranslations'
import { merge } from 'lodash'
import { useCallback, useEffect } from 'react'
import { apiErrors2Message } from 'utils/apiErrors'
import { actions, SystemMessage } from './systemMessageSlice'

/**
 * This hooks returns function which we can use to show messages
 *
 * Usage:
 * const showMessage = useShowMessage()
 * // in some logic
 * showMessage({ message: 'Some message', detail: 'Optional detail', type: 'success' })
 */
export const useShowMessage = () => {
  const dispatch = useAppDispatch()

  const showMessage = useCallback(
    (
      message: Pick<SystemMessage, 'type' | 'message' | 'detail' | 'timeout'>,
    ) => {
      // use Math.random for backward compatibility, e.g. Firefox older than v95
      const id = globalThis.crypto?.randomUUID?.() ?? Math.random().toString()

      const msg = { ...message, id, time: Date.now() }
      dispatch(actions.addMessage(msg))

      return msg
    },
    [dispatch],
  )

  return showMessage
}

const combinedFieldTranslations = merge(
  {},
  translations.event,
  translations.opportunity,
)

/**
 * Given error from rtk-query (or probably fetch), and optional message, this displays the error message
 *
 * Usage:
 * const { data, ...state } = api.endpoints.endpoint.useQuery()
 * useShowApiErrorMessage(state.error, 'Displayed error message')
 */
export const useShowApiErrorMessage = (
  error: FetchBaseQueryError | SerializedError | undefined,
  message = 'Něco se nepovedlo',
  fieldTranslations = combinedFieldTranslations,
  genericTranslations = translations.generic,
  // limit = Infinity,
) => {
  const showMessage = useShowMessage()
  useEffect(() => {
    let detail = ''

    if (error && 'status' in error) {
      detail += apiErrors2Message(
        error,
        fieldTranslations,
        genericTranslations,
        // limit,
      )
    } else {
      detail += `${error?.code ?? ''} ${error?.name ?? ''}\n${
        error?.message ?? ''
      }`
    }
    if (error)
      showMessage({
        message,
        detail,
        type: 'error',
      })
  }, [error, fieldTranslations, genericTranslations, message, showMessage])
}
