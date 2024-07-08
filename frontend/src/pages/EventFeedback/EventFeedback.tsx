import { api } from 'app/services/bis'
import { Error, Loading, PageHeader } from 'components'
import { useCurrentUser } from 'hooks/currentUser'
import { useTitle } from 'hooks/title'
import { FC } from 'react'
import { FaRegCalendarAlt } from 'react-icons/fa'
import { GrLocation } from 'react-icons/gr'
import { useParams } from 'react-router-dom'
import { formatDateRange } from 'utils/helpers'
import styles from './EventFeedback.module.scss'
import { EventFeedbackForm } from './EventFeedbackForm'

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
    return <Error message="Tato akce ještě nesbírá zpětnou vazbu." />
  }

  const handleCancel = () => {
    // TODO where to return ?
    globalThis.location.href = `https://brontosaurus.cz/akce/${eventId}/`
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
      <EventFeedbackForm
        id={eventId}
        feedbackForm={event.record.feedback_form}
        user={user}
        onCancel={handleCancel}
      />
    </div>
  )
}
