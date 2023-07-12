import { useAppSelector } from 'app/hooks'
import { SystemMessage } from './SystemMessage'
import styles from './SystemMessages.module.scss'
import { selectMessages } from './systemMessageSlice'

export const SystemMessages = () => {
  const messages = useAppSelector(selectMessages)
  return (
    <ul className={styles.container}>
      {messages.map(message => (
        <li key={message.id}>
          <SystemMessage {...message} />
        </li>
      ))}
    </ul>
  )
}
