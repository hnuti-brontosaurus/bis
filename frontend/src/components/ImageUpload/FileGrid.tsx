import { ReactNode } from 'react'
import styles from './ImageUpload.module.scss'

/**
 * The look shared by the uploads that keep files in a form and those that
 * save them right away; `children` are `FileGridItem`s, `add` the tile that
 * picks new files.
 */
export const FileGrid = ({
  children,
  add,
}: {
  children: ReactNode
  add: ReactNode
}) => (
  <ul className={styles.imageList}>
    {children}
    <li className={styles.imageItem}>{add}</li>
  </ul>
)
