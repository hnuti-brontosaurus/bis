import classNames from 'classnames'
import { Help } from 'components'
import { ForwardedRef, forwardRef, InputHTMLAttributes, ReactNode } from 'react'
import styles from './IconSelect.module.scss'

interface IconSelectProps extends InputHTMLAttributes<HTMLInputElement> {
  text: ReactNode
  detail?: ReactNode
  help?: ReactNode
  icon: React.FunctionComponent<
    React.SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
  id: string
  smallIcon?: boolean
}

export const IconSelect = forwardRef(
  (
    {
      text,
      detail,
      help,
      icon,
      id,
      smallIcon,
      className,
      ...rest
    }: IconSelectProps,
    ref: ForwardedRef<HTMLInputElement>,
  ) => {
    const Icon = icon
    return (
      <div
        className={classNames(
          styles.iconItem,
          smallIcon && styles.smallIcon,
          className,
        )}
      >
        <input
          type="radio"
          id={id}
          ref={ref}
          {...rest}
          className={styles.input}
        />
        <label htmlFor={id} className={styles.label}>
          <div>
            <div className={styles.icon}>
              <Icon height={60} width={60} />
            </div>
          </div>
          <span className={styles.title}>
            {help && (
              <>
                <Help>{help}</Help>{' '}
              </>
            )}
            {text}
          </span>
          {detail && <span className={styles.detail}>{detail}</span>}
        </label>
      </div>
    )
  },
)

export const IconSelectGroup = ({
  children,
  className,
  color = 'green',
}: {
  children: ReactNode
  className?: string
  color?: 'green' | 'blue'
}) => {
  return (
    <div
      className={classNames(
        styles.group,
        className,
        color === 'blue' ? styles.blue : styles.green,
      )}
    >
      {children}
    </div>
  )
}
