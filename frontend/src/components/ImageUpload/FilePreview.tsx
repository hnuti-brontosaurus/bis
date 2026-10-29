import classNames from 'classnames'
import { FC } from 'react'
import { FaImage, FaPencilAlt } from 'react-icons/fa'
import { FileFallback } from './FileFallback'
import styles from './FilePreview.module.scss'

interface Props {
  url: string
  editable?: boolean
}

export const FilePreview: FC<Props> = ({ url, editable }) => (
  <div className={classNames(styles.imageWrapper, editable && styles.editable)}>
    <object data={url} className={styles.image}>
      <FileFallback Icon={FaImage}>(nelze zobrazit)</FileFallback>
    </object>
    {editable && (
      <div className={styles.editOverlay}>
        <FaPencilAlt size={26} />
      </div>
    )}
  </div>
)
