import { EventApplication, User } from 'app/services/bisTypes'
import { StyledModal } from 'components'
import { FC } from 'react'
import styles from './EmailListModal.module.scss'
import type * as original from 'app/services/testApi'

interface IEmailListModalProps {
  open: boolean
  onClose: () => void
  lists: {
    users: (EventApplication | User | original.User)[]
    title: string
  }[]
  title: string
}

export const EmailListModal: FC<IEmailListModalProps> = ({
  open,
  onClose,
  lists,
  title,
}) => {
  if (!open) return null

  return (
    <StyledModal
      open={open}
      onClose={() => {
        onClose()
      }}
      title={title}
    >
      <div
        onClick={e => {
          e.stopPropagation()
        }}
        className={styles.content}
      >
        <div className={styles.modalFormBox}>
          <div className={styles.emailList}>
            {lists?.map(
              (list: {
                users: (EventApplication | User | original.User)[]
                title: string
              }) => (
                <div className={styles.emailList} key={list.title}>
                  <div className={styles.emailListTitle}>{list.title}</div>
                  <div className={styles.emailListContent}>
                    {list.users?.map(
                      (
                        application: EventApplication | User | original.User,
                        index,
                      ) =>
                        `${index !== 0 ? ', ' : ''}${application.first_name} ${
                          application.last_name
                        } <${application.email}>`,
                    )}
                  </div>
                </div>
              ),
            )}
          </div>
        </div>
      </div>
    </StyledModal>
  )
}
