import { api } from 'app/services/bis'
import type { Event } from 'app/services/bisTypes'
import { Loading, UnscalablePaginatedList } from 'components'
import { useCurrentUser } from 'hooks/currentUser'
import { useTitle } from 'hooks/title'
import { UserEventTable } from 'user/UserEventTable'

export const UserRegisteredEvents = () => {
  useTitle('Akce na které jsem se přihlásil/a')
  const { data: currentUser } = useCurrentUser()
  const { data: events } = api.endpoints.readRegisteredEvents.useQuery({
    userId: currentUser!.id,
    pageSize: 10000,
  })

  if (!events) return <Loading>Nahráváme akce</Loading>

  return (
    <UnscalablePaginatedList<Event>
      data={events.results}
      table={UserEventTable}
    />
  )
}
