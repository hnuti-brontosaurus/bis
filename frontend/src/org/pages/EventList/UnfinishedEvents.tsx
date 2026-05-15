import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import { Loading, PAGINATED_LIST_PAGE_SIZE, PaginatedList } from 'components'
import { useCurrentUser } from 'hooks/currentUser'
import { useSearchParamsState } from 'hooks/searchParamsState'
import { useTitle } from 'hooks/title'
import { EventTable } from 'org/components'

export const UnfinishedEvents = () => {
  useTitle('Moje nevyplněné akce')
  const { data: currentUser } = useCurrentUser()
  const [page, setPage] = useSearchParamsState('s', 1, Number)

  const { data: events } = api.endpoints.readOrganizedEvents.useQuery(
    currentUser
      ? {
          userId: currentUser.id,
          page,
          pageSize: PAGINATED_LIST_PAGE_SIZE,
          is_archived: false,
          is_closed: false,
          is_canceled: false,
        }
      : skipToken,
  )

  if (!events) return <Loading>Stahujeme akce...</Loading>

  return (
    <PaginatedList
      table={EventTable}
      data={events.results}
      totalCount={events.count}
      page={page}
      pageSize={PAGINATED_LIST_PAGE_SIZE}
      onPageChange={setPage}
      action="finish"
      columnsToHideOnMobile={[3, 4]}
    />
  )
}
