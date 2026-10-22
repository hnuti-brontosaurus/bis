import classNames from 'classnames'
import { ReactNode } from 'react'
import { FaTimes } from 'react-icons/fa'
import { DownloadLink } from './DownloadLink'
import styles from './ImageUpload.module.scss'

export const FileGridItem = ({
  children,
  url,
  onRemove,
}: {
  children: ReactNode
  url: string
  onRemove: () => void
}) => (
  <li className={styles.imageItem}>
    {children}
    <div className={styles.toolbar}>
      <DownloadLink url={url} />
      <button
        className={classNames(styles.button, styles.removeButton)}
        type="button"
        onClick={onRemove}
      >
        <FaTimes />
      </button>
    </div>
  </li>
)
