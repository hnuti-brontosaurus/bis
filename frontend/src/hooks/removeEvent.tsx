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

export const useRemoveEvent = () => {
  const [removeEvent, states] = api.endpoints.deleteEvent.useMutation()

  useShowApiErrorMessage(states.error, 'Nepodařilo se smazat akci')
  const showMessage = useShowMessage()

  const removeEventWithModal = async (event: { id: number; name: string }) => {
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
        title: `Mažeš akci ${event.name}`,
        message: 'Všechna data budou navždy ztracena. Chceš pokračovat?',
      })
    })
    if (isConfirmed) {
      await removeEvent(event).unwrap()
      showMessage({
        message: 'Akce byla úspěšně smazána',
        type: 'success',
      })
    }
  }
  return [removeEventWithModal, states] as const
}
