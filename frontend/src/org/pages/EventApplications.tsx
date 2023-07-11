import { Event } from 'app/services/bisTypes'
import { Breadcrumbs } from 'components'
import { ParticipantsStep } from 'org/components/EventForm/steps/ParticipantsStep'
import { useOutletContext } from 'react-router-dom'

export const EventApplications = () => {
  const { event } = useOutletContext<{ event: Event }>()
  return (
    <>
      <Breadcrumbs eventName={event.name} />
      <ParticipantsStep event={event} />
    </>
  )
}
