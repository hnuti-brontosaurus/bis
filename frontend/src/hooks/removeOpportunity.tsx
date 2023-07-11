import { api } from 'app/services/bis'
import { Actions, Button } from 'components'
import modalStyles from 'components/StyledModal/StyledModal.module.scss'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { confirmAlert } from 'react-confirm-alert'
import 'react-confirm-alert/src/react-confirm-alert.css'

// open modal before before removing opportunity

export const useRemoveOpportunity = () => {
  const [removeOpportunity, states] =
    api.endpoints.deleteOpportunity.useMutation()

  useShowApiErrorMessage(states.error, 'Nepodařilo se smazat příležitost')
  const showMessage = useShowMessage()

  const removeOpportunityWithModal = async (opportunity: {
    id: number
    userId: string
    name: string
  }) => {
    // replace with custom ui
    const isConfirmed = await new Promise(resolve => {
      confirmAlert({
        customUI: ({ title, message, onClose }) => (
          // this modal component is copy-pasted from similar useRemoveEvent hook
          // TODO maybe dry it
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
        title: `Mažeš příležitost ${opportunity.name}`,
        message: 'Všechna data budou navždy ztracena. Chceš pokračovat?',
      })
    })
    if (isConfirmed) {
      await removeOpportunity(opportunity).unwrap()
      showMessage({
        message: 'Příležitost byla úspěšně smazána',
        type: 'success',
      })
      return true
    } else return false
  }
  return [removeOpportunityWithModal, states] as const
}
