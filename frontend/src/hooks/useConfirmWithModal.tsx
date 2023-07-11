import { Actions, Button } from 'components'
import modalStyles from 'components/StyledModal/StyledModal.module.scss'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { confirmAlert } from 'react-confirm-alert'
import 'react-confirm-alert/src/react-confirm-alert.css'

/**
 * A custom hook that shows a confirmation modal before executing a function.
 *
 * @param successMessage - Optional success message to show upon successful completion of the function.
 * @param errorMessage - Optional error message to show upon unsuccessful completion of the function.
 * @param title - The title of the confirmation modal.
 * @param message - The message to show in the confirmation modal.
 * @returns the confirmWithModal function
 */
export const useConfirmWithModal = ({
  successMessage,
  errorMessage,
  title,
  message,
}: {
  successMessage?: string
  errorMessage?: string
  title: string
  message: string
}) => {
  // Custom hook to show API error messages
  useShowApiErrorMessage(
    undefined,
    errorMessage || 'Nepodařilo se vykonat akci',
  )
  // Custom hook to show general messages
  const showMessage = useShowMessage()

  /**
   * Shows a confirmation modal before executing the given function.
   *
   * @param onConfirm - The function to execute if the user confirms the action.
   */
  const confirmWithModal = async (onConfirm: Function) => {
    // Show confirmation modal and wait for user input
    const isConfirmed = await new Promise(resolve => {
      confirmAlert({
        customUI: ({ title, message, onClose }) => (
          <div className={modalStyles.modal}>
            <div className={modalStyles.content}>
              <header className={modalStyles.modalTitleBox}>{title}</header>
              <div className={modalStyles.modalFormBox}>
                <div className={modalStyles.infoBox}>{message}</div>
                <Actions>
                  <Button
                    secondary
                    onClick={() => {
                      resolve(false)
                      onClose()
                    }}
                  >
                    Zruš
                  </Button>
                  <Button
                    danger
                    onClick={() => {
                      resolve(true)
                      onClose()
                    }}
                  >
                    Pokračuj
                  </Button>
                </Actions>
              </div>
            </div>
          </div>
        ),
        title,
        message,
      })
    })
    // If the user confirmed the action, execute the provided function and show the success message (if provided)
    if (isConfirmed) {
      await onConfirm()
      successMessage &&
        showMessage({
          message: successMessage,
          type: 'success',
        })
    }
  }
  return [confirmWithModal] as const
}
