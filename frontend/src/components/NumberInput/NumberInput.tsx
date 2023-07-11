import { forwardRef, InputHTMLAttributes } from 'react'
import { FaMinus, FaPlus } from 'react-icons/fa'
import { Overwrite } from 'utility-types'
import styles from './NumberInput.module.scss'

export const NumberInput = forwardRef<
  HTMLInputElement,
  Overwrite<
    InputHTMLAttributes<HTMLInputElement>,
    {
      value: number | undefined | null
      onChange: (value: number | undefined) => void
      min?: number
      max?: number
    }
  >
>(({ value, onChange, min = -Infinity, max = Infinity, ...props }, ref) => {
  return (
    <div className={styles.container}>
      <div
        className={styles.button}
        onClick={() => {
          onChange(typeof value === 'number' ? Math.max(value - 1, min) : 1)
        }}
      >
        <FaMinus />
      </div>
      <input
        ref={ref}
        className={styles.input}
        type="number"
        value={value ?? undefined}
        min={min}
        max={max}
        onChange={e =>
          onChange(
            e.target.value.length > 0 && !isNaN(Number(e.target.value))
              ? Number(e.target.value)
              : ('' as unknown as number),
          )
        }
        {...props}
      />
      <div
        className={styles.button}
        onClick={() => {
          onChange(typeof value === 'number' ? Math.min(value + 1, max) : 1)
        }}
      >
        <FaPlus />
      </div>
    </div>
  )
})
