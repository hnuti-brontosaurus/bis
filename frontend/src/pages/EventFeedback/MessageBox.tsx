import { FC, ReactNode } from 'react'
import styles from './MessageBox.module.scss'

export const MessageBox: FC<{ children: ReactNode }> = ({ children }) => (
  <div className={styles.main}>{children}</div>
)
