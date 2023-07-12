import type { PaginatedList } from 'app/services/bisTypes'
import { Event } from 'app/services/bisTypes'
import { UnscalablePaginatedList } from 'components'
import { useTitle } from 'hooks/title'
import { EventTable } from 'org/components'
import { useOutletContext } from 'react-router-dom'
import { getEventStatus } from 'utils/helpers'

export const UnfinishedEvents = () => {
  useTitle('Moje nevyplněné akce')
  const events = useOutletContext<PaginatedList<Event>>()

  // here we want events that haven't been finished, and are not drafts
  // TODO we'll need info from api what's draft and what's done
  // for now we just show the events without record

  const inputEvents = (events.results ?? []).filter(
    event => getEventStatus(event) === 'inProgress',
  )

  return (
    <UnscalablePaginatedList
      table={EventTable}
      data={inputEvents}
      action="finish"
      columnsToHideOnMobile={[3, 4]}
    />
  )
}
