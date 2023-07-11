import { Error, Loading } from 'components'
import { useAllowedToCreateEvent } from 'hooks/useAllowedToCreateEvent'
import { Outlet } from 'react-router-dom'

export const EventOrganizerOutlet = () => {
  const [canAddEvent, isLoading] = useAllowedToCreateEvent()

  if (isLoading) return <Loading>Ověřujeme Tvé role</Loading>

  return canAddEvent ? (
    <Outlet />
  ) : (
    <Error
      status={403}
      message="Nemáš dostatečná práva k TODO text organizátorskému přístupu"
    >
      TODO text
    </Error>
  )
}
