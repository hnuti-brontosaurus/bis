import classNames from 'classnames'
import { FC } from 'react'
import { MdPhotoCamera } from 'react-icons/md'
import styles from './AddImageButton.module.scss'

interface Props {
  children: string
  colorTheme?: string
}

export const AddImageButton: FC<Props> = ({ children, colorTheme }) => (
  <div
    className={classNames(
      styles.button,
      colorTheme === 'opportunities' && styles.opportunitiesTheme,
    )}
  >
    <MdPhotoCamera size={60} />
    {children}
  </div>
)
