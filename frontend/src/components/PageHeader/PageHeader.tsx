import { ReactNode } from 'react'
import styles from './PageHeader.module.scss'

export const PageHeader = ({ children }: { children: ReactNode }) => (
  <h1 className={styles.header}>{children}</h1>
)
