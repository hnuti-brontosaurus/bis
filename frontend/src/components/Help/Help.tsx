import { ReactNode, useEffect, useRef, useState } from 'react'
import { GoInfo } from 'react-icons/go'
import Tooltip from 'react-tooltip-lite'
import styles from './Help.module.scss'

export const Help = ({ children }: { children: ReactNode }) => {
  const [isOpen, setIsOpen] = useState(false)

  const helpRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    const handleBodyClick = (e: MouseEvent) => {
      if (
        (helpRef?.current && helpRef.current.contains(e.target as Node)) ||
        (buttonRef?.current && buttonRef.current.contains(e.target as Node))
      ) {
        return
      }

      setIsOpen(false)
    }

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false)
      }
    }

    document.addEventListener('click', handleBodyClick)
    document.addEventListener('keydown', handleEscape)

    return () => {
      document.removeEventListener('click', handleBodyClick)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [])
  return (
    <Tooltip
      useDefaultStyles
      content={
        <div className={styles.tooltip} ref={helpRef}>
          {children}
        </div>
      }
      tagName="span"
      isOpen={isOpen}
    >
      <button
        type="button"
        ref={buttonRef}
        onClick={() => {
          setIsOpen(is => !is)
        }}
        className={styles.trigger}
      >
        <GoInfo />
      </button>
    </Tooltip>
  )
}
