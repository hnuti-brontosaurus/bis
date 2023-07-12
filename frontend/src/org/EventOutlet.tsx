import { Error, Loading } from 'components'
import { useReadFullEvent } from 'hooks/readFullEvent'
import { Outlet, useParams } from 'react-router-dom'

export const EventOutlet = () => {
  const params = useParams()
  const eventId = Number(params.eventId)

  const { data: event, isError, error } = useReadFullEvent(eventId)

  // when people write url with non-numeric id
  if (!eventId) return <Error status={400}>Zadejte platné id akce!</Error>

  if (isError) return <Error error={error}>Nepodařilo se nám najít akci</Error>

  if (!event) return <Loading>Stahujeme akci</Loading>

  return <Outlet context={{ event }} />
}
