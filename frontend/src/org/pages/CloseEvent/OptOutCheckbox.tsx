import { Actions, Button, StyledModal } from 'components'
import {
  ChangeEvent,
  ForwardedRef,
  forwardRef,
  ReactNode,
  useState,
} from 'react'
import { ChangeHandler } from 'react-hook-form'

interface Props {
  onChange: ChangeHandler
  onBlur: ChangeHandler
  name: string
  title: string
  message: ReactNode
}

export const OptOutCheckbox = forwardRef(
  (
    { onChange, onBlur, name, message, title }: Props,
    ref: ForwardedRef<HTMLInputElement>,
  ) => {
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
          title={title}
        >
          {message}
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
  },
)
