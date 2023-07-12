import classNames from 'classnames'
import React, { FC, ReactNode } from 'react'
import Tooltip from 'react-tooltip-lite'
import styles from './TableCellIconButton.module.scss'

interface CustomTableColumnProps {
  icon: FC<React.SVGProps<SVGSVGElement>>
  action?: () => void
  className?: string
  children?: ReactNode
  color?: string
  glowColor?: string
  tooltipContent?: ReactNode
  disabled?: boolean
  ariaLabel?: string
}

export const TableCellIconButton: FC<
  CustomTableColumnProps & React.HTMLAttributes<HTMLTableDataCellElement>
> = props => {
  const {
    icon: Icon,
    action,
    className,
    color,
    glowColor,
    children,
    tooltipContent,
    disabled,
    ariaLabel,
    ...rest
  } = props

  function handleIconClick(e: React.MouseEvent<HTMLSpanElement, MouseEvent>) {
    e.stopPropagation()
    e.preventDefault()
    if (action) {
      action()
    }
  }

  return (
    <td
      className={classNames(className, disabled && styles.disabledCell)}
      {...rest}
    >
      <Tooltip
        useDefaultStyles
        content={tooltipContent}
        tagName="span"
        // this hack prevents empty tooltip from showing up
        hoverDelay={tooltipContent ? 500 : 100000000}
      >
        <button
          aria-label={ariaLabel}
          className={styles.binIconContainer}
          onClick={handleIconClick}
          type="button"
        >
          <span
            className={styles.circle}
            style={{ backgroundColor: glowColor }}
          ></span>
          <Icon className={styles.iconHead} style={{ color }} />
        </button>
        {children}
      </Tooltip>
    </td>
  )
}
