import { FC, ReactNode, useState } from 'react'
import { Actions, Button, StyledModal } from 'components'

type Resolver = (confirm: boolean) => void

interface DialogProps {
  title: string
  confirmTitle: string
  cancelTitle: string
  children: ReactNode
  onConfirm?: () => void
  onCancel?: () => void
}

export const useSubmitConfirmation = () => {
  const [resolveConfirmation, setResolveConfirmation] =
    useState<Resolver | null>(null)

  const requireSubmitConfirmation = (): Promise<boolean> =>
    new Promise(resolve => setResolveConfirmation(() => resolve)) // setting resolve as is would interpret it as updater function

  const resolveSubmitConfirmation = (confirmed: boolean) => {
    if (resolveConfirmation) {
      resolveConfirmation(confirmed)
      setResolveConfirmation(null)
    }
  }

  const Dialog: FC<DialogProps> = ({
    title,
    children,
    cancelTitle,
    confirmTitle,
    onCancel,
    onConfirm,
  }) => {
    const handleCancel = () => {
      resolveSubmitConfirmation(false)
      onCancel?.()
    }
    const handleConfirm = () => {
      resolveSubmitConfirmation(true)
      onConfirm?.()
    }
    return (
      <StyledModal
        title={title}
        open={!!resolveConfirmation}
        onClose={handleCancel}
      >
        {children}
        <Actions>
          <Button secondary onClick={handleCancel}>
            {cancelTitle}
          </Button>
          <Button primary onClick={handleConfirm}>
            {confirmTitle}
          </Button>
        </Actions>
      </StyledModal>
    )
  }

  return [requireSubmitConfirmation, Dialog] as const
}
