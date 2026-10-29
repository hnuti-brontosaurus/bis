import classNames from 'classnames'
import { FC, ReactNode } from 'react'
import { FaDownload, FaTimes } from 'react-icons/fa'
import styles from './UploadedFile.module.scss'

interface Props {
  children: ReactNode
  downloadUrl: string
  onRemove: () => void
}

export const UploadedFile: FC<Props> = ({
  children,
  downloadUrl,
  onRemove,
}) => (
  <div className={styles.main}>
    {children}
    <div className={styles.toolbar}>
      <a
        href={downloadUrl}
        download={
          downloadUrl.match(/filename=(.*?);/)?.[1] ??
          downloadUrl.match(/[^/]*$/)?.[0] ??
          ''
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
