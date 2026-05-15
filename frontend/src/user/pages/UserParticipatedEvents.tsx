import { api } from 'app/services/bis'
import type { Event } from 'app/services/bisTypes'
import { Loading, PAGINATED_LIST_PAGE_SIZE, PaginatedList } from 'components'
import { useCurrentUser } from 'hooks/currentUser'
import { useSearchParamsState } from 'hooks/searchParamsState'
import { useTitle } from 'hooks/title'
import { UserEventTable } from 'user/UserEventTable'

export const UserParticipatedEvents = () => {
  useTitle('Akce kterých jsem se zúčastnil/a')
  const { data: currentUser } = useCurrentUser()
  const [page, setPage] = useSearchParamsState('s', 1, Number)
  const { data: events } = api.endpoints.readParticipatedEvents.useQuery({
    userId: currentUser!.id,
    page,
    pageSize: PAGINATED_LIST_PAGE_SIZE,
  })

  if (!events) return <Loading>Nahráváme akce</Loading>

  return (
    <PaginatedList<Event>
      data={events.results}
      totalCount={events.count}
      page={page}
      pageSize={PAGINATED_LIST_PAGE_SIZE}
      onPageChange={setPage}
      table={UserEventTable}
    />
  )
}
