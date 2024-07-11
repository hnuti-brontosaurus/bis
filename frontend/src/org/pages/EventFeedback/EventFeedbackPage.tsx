import { FC } from 'react'
import { Breadcrumbs } from 'components'
import { useOutletContext } from 'react-router-dom'
import { FullEvent } from 'app/services/bisTypes'
import { EventFeedback } from './EventFeedback'

export const EventFeedbackPage: FC = () => {
  const { event } = useOutletContext<{ event: FullEvent }>()

  return (
    <>
      <Breadcrumbs eventName={event.name} />
      <EventFeedback event={event} />
    </>
  )
}
