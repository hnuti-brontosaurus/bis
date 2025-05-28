import { ChangeEvent, FC, Ref, useState } from 'react'
import { Actions, Button, StyledModal } from 'components'
import { ChangeHandler } from 'react-hook-form'

interface Props {
  ref: Ref<HTMLInputElement>
  onChange: ChangeHandler
  onBlur: ChangeHandler
  name: string
  message: string
}

export const OptOutCheckbox: FC<Props> = ({
  ref,
  onChange,
  onBlur,
  name,
  message,
}) => {
  const [confirmedEvent, setConfirmedEvent] =
    useState<ChangeEvent<HTMLInputElement> | null>(null)
  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (!event.target.checked) {
      setConfirmedEvent(event)
    } else {
      onChange(event)
    }
  }
  const cancelChange = () => {
    if (confirmedEvent) {
      confirmedEvent.target.checked = true
      setConfirmedEvent(null)
    }
  }
  const confirmChange = () => {
    if (confirmedEvent) {
      onChange(confirmedEvent)
      setConfirmedEvent(null)
    }
  }

  return (
    <>
      <input
        type="checkbox"
        ref={ref}
        onChange={handleChange}
        onBlur={onBlur}
        name={name}
      />
      <StyledModal
        open={!!confirmedEvent}
        onClose={cancelChange}
        title={message}
      >
        <Actions>
          <Button secondary onClick={cancelChange}>
            Ne
          </Button>
          <Button danger onClick={confirmChange}>
            Ano
          </Button>
        </Actions>
      </StyledModal>
    </>
  )
}
