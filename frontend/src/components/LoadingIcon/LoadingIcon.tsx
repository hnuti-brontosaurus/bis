import classNames from 'classnames'
import type { IconType } from 'react-icons'
import { RiLoader4Fill } from 'react-icons/ri'
import styles from './LoadingIcon.module.scss'

export const LoadingIcon: IconType = ({ className, ...props }) => (
  <RiLoader4Fill className={classNames(className, styles.icon)} {...props} />
)
