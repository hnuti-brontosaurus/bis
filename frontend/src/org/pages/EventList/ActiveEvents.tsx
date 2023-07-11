import type { Event, PaginatedList } from 'app/services/bisTypes'
import { UnscalablePaginatedList } from 'components'
import { useTitle } from 'hooks/title'
import { EventTable } from 'org/components'
import { useOutletContext } from 'react-router-dom'
import { getEventStatus } from 'utils/helpers'

export const ActiveEvents = () => {
  useTitle('Moje aktuální akce')
  const events = useOutletContext<PaginatedList<Event>>()

  // here we want to show events that are not older than "next year June"
  const inputEvents = (events.results ?? []).filter(
    event => getEventStatus(event) !== 'closed',
  )

  return (
    <UnscalablePaginatedList
      table={EventTable}
      data={inputEvents}
      columnsToHideOnMobile={[3, 4]}
    />
  )
}
