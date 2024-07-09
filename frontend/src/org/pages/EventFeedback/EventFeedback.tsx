import { FC } from 'react'
import { Breadcrumbs } from 'components'
import { useOutletContext } from 'react-router-dom'
import { FullEvent } from 'app/services/bisTypes'

export const EventFeedback: FC = () => {
  const { event } = useOutletContext<{ event: FullEvent }>()
  return (
    <>
      <Breadcrumbs eventName={event.name} />
    </>
  )
}
