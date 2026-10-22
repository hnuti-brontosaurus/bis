import classNames from 'classnames'
import { FaImage, FaPencilAlt } from 'react-icons/fa'
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
      <div className={styles.fallback}>
        <FaImage size={60} />
        (nelze zobrazit)
      </div>
    </object>
    {editable && (
      <div className={styles.editOverlay}>
        <FaPencilAlt size={26} />
      </div>
    )}
  </div>
)
