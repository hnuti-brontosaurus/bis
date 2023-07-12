import { FC } from 'react'
import { MdClose } from 'react-icons/md'

import Modal from 'react-modal'
import styles from './StyledModal.module.scss'

interface IShowApplicationModalProps {
  open: boolean
  onClose: () => void
  title?: string
  children: any
}

export const StyledModal: FC<IShowApplicationModalProps> = ({
  open,
  onClose,
  title,
  children,
}) => {
  if (!open) return null

  return (
    <Modal
      isOpen={open}
      onRequestClose={onClose}
      contentLabel={title}
      className={styles.modal}
      overlayClassName={styles.overlay}
      appElement={document.getElementById('root') as HTMLElement}
    >
      <div className={styles.content}>
        <div className={styles.modalTitleBox}>
          <div className={styles.showUserApplicationNameBox}>
            {title ? <h2>{title}</h2> : null}
            <MdClose
              className={styles.closeIcon}
              size="1.5em"
              onClick={onClose}
            />
          </div>
        </div>
        <div className={styles.modalFormBox}>{children}</div>
      </div>
    </Modal>
  )
}
