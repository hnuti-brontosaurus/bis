import { useAppDispatch } from 'app/hooks'
import classNames from 'classnames'
import { useEffect } from 'react'
import { FaTimes } from 'react-icons/fa'
import { Optional } from 'utility-types'
import styles from './SystemMessage.module.scss'
import {
  actions,
  SystemMessage as SystemMessageType,
} from './systemMessageSlice'

// default dismiss timeouts per message type; error toasts stay up longer
// so they can actually be read before disappearing
const DEFAULT_TIMEOUTS = {
  success: 4_000,
  info: 6_000,
  warning: 8_000,
  error: 12_000,
} as const

export const SystemMessage = ({
  id,
  type,
  message,
  detail,
  timeout,
}: Optional<SystemMessageType, 'time'>) => {
  const dispatch = useAppDispatch()

  const dismissAfter = timeout ?? DEFAULT_TIMEOUTS[type]

  // remove message after a timeout passes
  useEffect(() => {
    if (dismissAfter > 0) {
      const timeoutId = setTimeout(() => {
        dispatch(actions.removeMessage(id))
      }, dismissAfter)
      return () => {
        clearTimeout(timeoutId)
      }
    }
  }, [dismissAfter, dispatch, id])

  const handleCloseMessage = () => {
    dispatch(actions.removeMessage(id))
  }

  return (
    <div
      className={classNames(
        styles.container,
        type === 'info' && styles.info,
        type === 'error' && styles.error,
        type === 'success' && styles.success,
        type === 'warning' && styles.warning,
      )}
    >
      <header className={styles.header}>
        {message}
        <button onClick={handleCloseMessage}>
          <FaTimes />
        </button>
      </header>
      {detail && <div className={styles.detail}>{detail}</div>}
    </div>
  )
}
