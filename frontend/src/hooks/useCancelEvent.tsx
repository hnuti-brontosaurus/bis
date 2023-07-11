import { api } from 'app/services/bis'
import { Actions, Button } from 'components'
import modalStyles from 'components/StyledModal/StyledModal.module.scss'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { confirmAlert } from 'react-confirm-alert'
import 'react-confirm-alert/src/react-confirm-alert.css'

// open modal before before removing event

export const useCancelEvent = () => {
  const [updateEvent, states] = api.endpoints.updateEvent.useMutation()

  useShowApiErrorMessage(states.error, 'Nepodařilo se zrušit akci')
  const showMessage = useShowMessage()

  const cancelEventWithModal = async (event: { id: number; name: string }) => {
    // replace with custom ui
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
                    Ne
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
        title: `Rušíš akci ${event.name}`,
        message:
          'Akce bude zrušena a nebude možné se na ni přihlásit. Chceš pokračovat? (Bude možné to změnit zpátky.)',
      })
    })
    if (isConfirmed) {
      await updateEvent({ id: event.id, event: { is_canceled: true } }).unwrap()
      showMessage({
        message: `Akce ${event.name} byla zrušena`,
        type: 'success',
      })
    }
  }
  return [cancelEventWithModal, states] as const
}

export const useRestoreCanceledEvent = () => {
  const [updateEvent, states] = api.endpoints.updateEvent.useMutation()

  useShowApiErrorMessage(states.error, 'Nepodařilo se obnovit zrušenou akci')
  const showMessage = useShowMessage()

  const restoreCanceledEventWithModal = async (event: {
    id: number
    name: string
  }) => {
    // replace with custom ui
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
                    Ne
                  </Button>
                  <Button
                    primary
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
        title: `Obnovuješ akci ${event.name}`,
        message: 'Chceš pokračovat?',
      })
    })
    if (isConfirmed) {
      await updateEvent({
        id: event.id,
        event: { is_canceled: false },
      }).unwrap()
      showMessage({
        message: `Akce ${event.name} byla obnovena`,
        type: 'success',
      })
    }
  }
  return [restoreCanceledEventWithModal, states] as const
}
