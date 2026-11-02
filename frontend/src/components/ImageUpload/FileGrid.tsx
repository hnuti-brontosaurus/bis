import { FC, ReactNode } from 'react'
import styles from './FileGrid.module.scss'

interface Props {
  children: ReactNode
}

export const FileGrid: FC<Props> = ({ children }) => (
  <ul className={styles.list}>{children}</ul>
)

export const FileGridItem: FC<Props> = ({ children }) => (
  <li className={styles.item}>{children}</li>
)
