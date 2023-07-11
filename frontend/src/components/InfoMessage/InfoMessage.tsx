import { useAppDispatch, useAppSelector } from 'app/hooks'
import { actions, selectInfoMessageVisibility } from 'features/ui/uiSlice'
import { ReactNode } from 'react'
import { FaTimes } from 'react-icons/fa'
import styles from './InfoMessage.module.scss'

export const InfoMessage = ({
  closable = false,
  children,
  id,
}: {
  closable?: boolean
  children: ReactNode
  id: string
}) => {
  const isVisible = useAppSelector(state =>
    selectInfoMessageVisibility(state, id),
  )
  const dispatch = useAppDispatch()
  const hide = () => dispatch(actions.hideInfoMessage(id))
  return isVisible ? (
    <div className={styles.container}>
      <div className={styles.message}>{children}</div>
      {closable && (
        <button className={styles.closeButton} onClick={hide}>
          <FaTimes />
        </button>
      )}
    </div>
  ) : null
}
