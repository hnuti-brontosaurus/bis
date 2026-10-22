import classNames from 'classnames'
import { FaDownload } from 'react-icons/fa'
import styles from './ImageUpload.module.scss'

export const DownloadLink = ({ url }: { url: string }) => {
  const fileName =
    url.match(/filename=(.*?);/)?.[1] ?? url.match(/[^/]*$/)?.[0] ?? ''
  return (
    <a
      href={url}
      download={fileName}
      className={classNames(styles.button, styles.downloadButton)}
    >
      <FaDownload />
    </a>
  )
}
