import classNames from 'classnames'
import React, { FC } from 'react'
import Tooltip from 'react-tooltip-lite'
import styles from '../ParticipantsStep.module.scss'

interface Props {
  value: boolean
  onChange: (value: boolean) => void
}

export const PaidForCheckbox: FC<Props> = ({ value, onChange }) => (
  <Tooltip useDefaultStyles content="zaplaceno" tagName="span" hoverDelay={500}>
    <label className={classNames('checkboxLabel', styles.paidForCheckbox)}>
      <input
        type="checkbox"
        onChange={e => onChange(e.target.checked)}
        checked={value}
      />
    </label>
  </Tooltip>
)
