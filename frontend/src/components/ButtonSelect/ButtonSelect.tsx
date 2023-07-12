import classNames from 'classnames'
import {
  ForwardedRef,
  forwardRef,
  InputHTMLAttributes,
  ReactElement,
  ReactNode,
} from 'react'
import styles from './ButtonSelect.module.scss'

interface ButtonSelectProps extends InputHTMLAttributes<HTMLInputElement> {
  label: ReactNode
  id: string
  icon: ReactElement<any, any>
}

export const ButtonSelect = forwardRef(
  (
    { id, label, icon, ...rest }: ButtonSelectProps,
    ref: ForwardedRef<HTMLInputElement>,
  ) => {
    return (
      <div className={styles.buttonSelect}>
        <input
          type="radio"
          id={id}
          ref={ref}
          {...rest}
          className={styles.input}
        />
        <label htmlFor={id} className={styles.label}>
          {/* @ts-ignore */}
          <div className={styles.icon}>{icon}</div>
          <div className={styles.labelText}>{label}</div>
        </label>
      </div>
    )
  },
)

export const ButtonSelectGroup = ({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) => {
  return <div className={classNames(styles.group, className)}>{children}</div>
}
