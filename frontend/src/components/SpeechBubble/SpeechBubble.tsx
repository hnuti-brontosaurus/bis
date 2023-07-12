import classNames from 'classnames'
import { ReactNode } from 'react'
import styles from './SpeechBubble.module.scss'

interface SpeechBubbleProps {
  hideTail?: boolean
  className?: string
  children?: ReactNode
  id?: string
  left?: boolean
}

export const SpeechBubble = ({
  hideTail,
  className,
  children,
  id,
  left,
}: SpeechBubbleProps) => {
  return (
    <div
      className={classNames(
        styles.bubbleRectangle,
        hideTail && styles.hideTail,
        className,
        left && styles.left,
      )}
      id={id}
    >
      {children}
    </div>
  )
}
