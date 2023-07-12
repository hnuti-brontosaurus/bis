import dayjs from 'dayjs'
import merge from 'lodash/merge'
import { forwardRef, useEffect } from 'react'
import { Noop } from 'react-hook-form'
import * as yup from 'yup'

type Birthdate = {
  day: string
  month: string
  year: string
}

export const birthdayValidation = yup
  .string()
  .nullable()
  .test({
    test: date =>
      !date ||
      dayjs(
        date,
        ['YYYY-M-D', 'YYYY-MM-DD', 'YYYY-MM-D', 'YYYY-M-DD'],
        true,
      ).isValid(),
    message: 'Datum není správně zadáno nebo neexistuje',
  })

const splitBirthday = (birthday: string | null): Birthdate => {
  const [year, month, day] = birthday?.split('-') ?? ['', '', '']
  return { year: year ?? '', month: month ?? '', day: day ?? '' }
}
const joinBirthday = ({ year, month, day }: Birthdate): string | null => {
  if (!(year || month || day)) return null
  return [year, month, day].join('-')
}

export const BirthdayInput = forwardRef<
  HTMLInputElement,
  {
    onChange: (value: string | null) => void
    onBlur: Noop
    value: string
    name: string
  }
>(({ value, onChange, name }, ref) => {
  const { day, month, year } = splitBirthday(value)

  const handleChange = (date: Partial<Birthdate>) => {
    const birthday = joinBirthday(merge({ day, month, year }, date))
    onChange(birthday)
  }

  useEffect(() => {
    onChange(joinBirthday({ day, month, year }))
  }, [day, month, onChange, year])

  return (
    <div>
      <input
        ref={ref}
        type="text"
        name={`${name}-day`}
        placeholder="DD"
        maxLength={2}
        size={2}
        value={day}
        onChange={e => handleChange({ day: e.target.value })}
      />
      .
      <input
        type="text"
        name={`${name}-month`}
        placeholder="MM"
        maxLength={2}
        size={2}
        value={month}
        onChange={e => handleChange({ month: e.target.value })}
      />
      .
      <input
        type="text"
        name={`${name}-year`}
        placeholder="RRRR"
        maxLength={4}
        size={4}
        value={year}
        onChange={e => handleChange({ year: e.target.value })}
      />
    </div>
  )
})
