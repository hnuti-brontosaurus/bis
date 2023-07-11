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

export const SystemMessage = ({
  id,
  type,
  message,
  detail,
  timeout = 5000,
}: Optional<SystemMessageType, 'time'>) => {
  const dispatch = useAppDispatch()

  // remove message after a timeout passes
  useEffect(() => {
    if (timeout > 0) {
      const timeoutId = setTimeout(() => {
        dispatch(actions.removeMessage(id))
      }, timeout)
      return () => {
        clearTimeout(timeoutId)
      }
    }
  }, [dispatch, id, timeout])

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
