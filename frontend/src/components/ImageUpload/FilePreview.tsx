import classNames from 'classnames'
import { FaImage, FaPencilAlt } from 'react-icons/fa'
import { FileFallback } from './FileFallback'
import styles from './ImageUpload.module.scss'

export const FilePreview = ({
  url,
  editable,
}: {
  url: string
  editable?: boolean
}) => (
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
