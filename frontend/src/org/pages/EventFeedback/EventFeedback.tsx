import { FC, useState } from 'react'
import { api } from 'app/services/bis'
import { Loading, StyledModal } from 'components'
import { EventFeedbackRead } from 'app/services/testApi'
import { FullEvent } from 'app/services/bisTypes'
import { EventFeedbackTable } from './EventFeedbackTable'
import styles from './EventFeedback.module.scss'
import { FeedbackDetail } from './FeedbackDetail'

export const EventFeedback: FC<{ event: FullEvent }> = ({ event }) => {
  const { data: feedbacks } = api.endpoints.readEventFeedbacks.useQuery({
    eventId: event.id,
  })
  const { data: inquiries } = api.endpoints.readEventFeedbackInquiries.useQuery(
    { eventId: event.id, pageSize: 1000 }, // TODO is there a better way to load all?
  )
  const [displayedFeedback, setDisplayedFeedback] = useState<
    EventFeedbackRead | undefined
  >(undefined)

  if (!(feedbacks && feedbacks.results && inquiries && inquiries.results)) {
    return <Loading>Nahráváme zpětnou vazbu</Loading>
  }

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Zpětná vazba</h2>
      <EventFeedbackTable
        inquiries={inquiries.results}
        feedbacks={feedbacks.results}
        onRowClick={selected =>
          setDisplayedFeedback(
            feedbacks.results.find(({ id }) => id === selected),
          )
        }
      />
      <StyledModal
        open={!!displayedFeedback}
        onClose={() => setDisplayedFeedback(undefined)}
        title={`Zpětná vazba na akci ${event.name}`}
      >
        {displayedFeedback && <FeedbackDetail feedback={displayedFeedback} />}
      </StyledModal>
    </div>
  )
}
