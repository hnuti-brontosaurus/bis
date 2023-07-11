import { useAppSelector } from 'app/hooks'
import { Error, Loading } from 'components'
import { selectLoggingOut } from 'features/auth/authSlice'
import { useCurrentUser } from 'hooks/currentUser'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { AuthenticatedLayout } from './AuthenticatedLayout'

export const AuthenticatedOutlet = () => {
  const { isAuthenticated, error, data: user } = useCurrentUser()
  const location = useLocation()

  const isLoggingOut = useAppSelector(selectLoggingOut)

  if (isAuthenticated) {
    return (
      <AuthenticatedLayout>
        {user ? (
          isLoggingOut ? (
            <Loading hideHeader>Probíhá odhlašování...</Loading>
          ) : (
            <Outlet />
          )
        ) : error ? (
          <Error error={error} />
        ) : (
          <Loading>Ověřujeme uživatele</Loading>
        )}
      </AuthenticatedLayout>
    )
  } else {
    // next location will be the current, or empty
    const next = ['', '/'].includes(location.pathname)
      ? ''
      : `?next=${encodeURIComponent(location.pathname)}`
    return <Navigate to={`/login${next}`} replace />
  }
}
