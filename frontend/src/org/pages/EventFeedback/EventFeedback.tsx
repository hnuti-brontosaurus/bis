import { FC } from 'react'
import { api } from 'app/services/bis'
import { Loading } from 'components'
import { EventFeedbackTable } from './EventFeedbackTable'
import styles from './EventFeedback.module.scss'

export const EventFeedback: FC<{ eventId: number }> = ({ eventId }) => {
  const { data: feedbacks } = api.endpoints.readEventFeedbacks.useQuery({
    eventId,
  })
  const { data: inquiries } = api.endpoints.readEventFeedbackInquiries.useQuery(
    { eventId },
  )

  if (!(feedbacks && feedbacks.results && inquiries && inquiries.results)) {
    return <Loading>Nahráváme zpětnou vazbu</Loading>
  }

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Zpětná vazba</h2>
      <EventFeedbackTable
        inquiries={inquiries.results}
        feedbacks={feedbacks.results}
      />
    </div>
  )
}
