import { Loading } from 'components'
import { useCurrentUser } from 'hooks/currentUser'
import { Navigate, Outlet, useSearchParams } from 'react-router-dom'
import { UnauthenticatedLayout } from './UnauthenticatedLayout'

export const UnauthenticatedOutlet = () => {
  const { data: user, isAuthenticated } = useCurrentUser()
  const [searchParams] = useSearchParams()

  if (user) {
    const redirect = searchParams.get('next') ?? '/'

    const reload = searchParams.get('reload')

    if (typeof reload === 'string') {
      globalThis.location.href = redirect
      return null
    } else {
      return <Navigate to={redirect} replace />
    }
  } else if (isAuthenticated) {
    return <Loading>Připravujeme aplikaci</Loading>
  } else {
    return (
      <UnauthenticatedLayout>
        <Outlet />
      </UnauthenticatedLayout>
    )
  }
}
