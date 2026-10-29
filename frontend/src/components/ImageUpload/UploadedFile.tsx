import classNames from 'classnames'
import { ReactNode } from 'react'
import { FaDownload, FaTimes } from 'react-icons/fa'
import styles from './UploadedFile.module.scss'

export const UploadedFile = ({
  children,
  url,
  onRemove,
}: {
  children: ReactNode
  url: string
  onRemove: () => void
}) => (
  <div className={styles.main}>
    {children}
    <div className={styles.toolbar}>
      <a
        href={url}
        download={
          url.match(/filename=(.*?);/)?.[1] ?? url.match(/[^/]*$/)?.[0] ?? ''
        }
        className={classNames(styles.button, styles.downloadButton)}
      >
        <FaDownload />
      </a>
      <button
        className={classNames(styles.button, styles.removeButton)}
        type="button"
        onClick={onRemove}
      >
        <FaTimes />
      </button>
    </div>
  </div>
)
