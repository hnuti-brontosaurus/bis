import { FC } from 'react'
import { IconType } from 'react-icons'
import styles from './FileFallback.module.scss'

interface Props {
  children: string
  Icon: IconType
}

export const FileFallback: FC<Props> = ({ children, Icon }) => (
  <div className={styles.main}>
    <Icon size={60} />
    {children}
  </div>
)
