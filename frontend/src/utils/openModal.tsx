import modalStyles from 'components/StyledModal/StyledModal.module.scss'
import { ReactNode } from 'react'
import { confirmAlert } from 'react-confirm-alert'
import 'react-confirm-alert/src/react-confirm-alert.css'

/**
 * Opens a modal and resolves with the value its content passes to `close`, or
 * with null when it is dismissed by Escape or a click outside.
 */
export const openModal = <T,>({
  title,
  message,
  render,
}: {
  title: string
  message: string
  render: (close: (value: T | null) => void) => ReactNode
}): Promise<T | null> =>
  new Promise(resolve => {
    confirmAlert({
      customUI: ({ onClose }) => (
        <div className={modalStyles.modal}>
          <div className={modalStyles.content}>
            <header className={modalStyles.modalTitleBox}>{title}</header>
            <div className={modalStyles.modalFormBox}>
              <div className={modalStyles.infoBox}>{message}</div>
              {render(value => {
                resolve(value)
                onClose()
              })}
            </div>
          </div>
        </div>
      ),
      // also runs after `close`, where resolving again is a no-op
      willUnmount: () => resolve(null),
    })
  })
