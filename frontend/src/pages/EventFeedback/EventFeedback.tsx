import { api } from 'app/services/bis'
import { EventFeedback as EventFeedbackShape } from 'app/services/testApi'
import { Actions, Button, Error, Loading, PageHeader } from 'components'
import { useShowApiErrorMessage } from 'features/systemMessage/useSystemMessage'
import { useCurrentUser } from 'hooks/currentUser'
import { useTitle } from 'hooks/title'
import { FC } from 'react'
import { FaRegCalendarAlt } from 'react-icons/fa'
import { GrLocation } from 'react-icons/gr'
import { useParams } from 'react-router-dom'
import { formatDateRange } from 'utils/helpers'
import {
  useClearPersistentForm,
  useDirectPersistForm,
  usePersistentFormData,
} from 'hooks/persistForm'
import styles from './EventFeedback.module.scss'
import { EventFeedbackForm } from './EventFeedbackForm'
import { MessageBox } from './MessageBox'

export type EventFeedbackWithStep = EventFeedbackShape & {
  step: 'progress' | 'finished'
}

export const EventFeedback: FC = () => {
  // TODO next search param ?

  const params = useParams()
  const eventId = Number(params.eventId)

  const { data: user, isAuthenticated } = useCurrentUser()

  const {
    data: event,
    isError: isEventError,
    error: eventError,
  } = api.endpoints.readWebEvent.useQuery({ id: eventId })

  useTitle(`Zpětná vazba na akci ${event?.name ?? ''}`)

  const formValues = usePersistentFormData(
    'feedback',
    String(eventId),
  ) as EventFeedbackWithStep
  const persistValue = useDirectPersistForm('feedback', String(eventId))
  const clearForm = useClearPersistentForm('feedback', String(eventId))

  const [createFeedback, { error: saveError }] =
    api.endpoints.createEventFeedback.useMutation()
  useShowApiErrorMessage(
    saveError,
    'Nepodařilo se nám uložit zpětnou vazbu. Zkuste to znovu.',
  )

  if (isAuthenticated && !user) {
    return <Loading>Ověřujeme uživatele</Loading>
  }
  if (isEventError) {
    return <Error error={eventError} />
  }
  if (!event) {
    return <Loading>Připravujeme zpětnou vazbu</Loading>
  }
  if (!event?.record?.feedback_form) {
    return (
      <Error message="Otázky pro zpětnou vazbu nejsou uložené. Pokud jsi tento odkaz dostal/a od organizátorů akce, kontaktuj je, prosím." />
    )
  }

  const handleSubmit = async (feedback: EventFeedbackShape) => {
    await createFeedback({ feedback, eventId }).unwrap()
    persistValue({ step: 'finished' })
  }

  return (
    <div>
      <PageHeader>Zpětná vazba na akci {event.name}</PageHeader>
      <div className={styles.infoBox}>
        <div>
          <FaRegCalendarAlt /> {formatDateRange(event.start, event.end)}
        </div>
        <div>
          <GrLocation /> {event.location?.name}
        </div>
      </div>
      {formValues?.step === 'finished' ? (
        <div>
          <MessageBox>
            {event.record.feedback_form.after_submit_text}
          </MessageBox>
          <Actions>
            <Button primary onClick={clearForm}>
              Další zpětná vazba
            </Button>
          </Actions>
        </div>
      ) : (
        <EventFeedbackForm
          id={eventId}
          feedbackForm={event.record.feedback_form}
          user={user}
          onSubmit={handleSubmit}
          onCancel={clearForm}
        />
      )}
    </div>
  )
}
