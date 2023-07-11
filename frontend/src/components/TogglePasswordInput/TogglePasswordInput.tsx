import classNames from 'classnames'
import { forwardRef, InputHTMLAttributes, useState } from 'react'
import { FaRegEye, FaRegEyeSlash } from 'react-icons/fa'
import styles from './TogglePasswordInput.module.scss'

export const TogglePasswordInput = forwardRef<
  HTMLInputElement,
  Omit<InputHTMLAttributes<HTMLInputElement>, 'type'>
>(({ className, ...props }, ref) => {
  const [visible, setVisible] = useState(false)
  return (
    <div className={classNames(className, styles.wrapper)}>
      <div className={styles.innerWrapper}>
        <input
          {...props}
          className={classNames(styles.input)}
          type={visible ? 'text' : 'password'}
          ref={ref}
        />
        <button
          className={styles.toggleButton}
          type="button"
          onClick={() => setVisible(v => !v)}
        >
          {visible ? <FaRegEyeSlash size={25} /> : <FaRegEye size={25} />}
        </button>
      </div>
    </div>
  )
})
