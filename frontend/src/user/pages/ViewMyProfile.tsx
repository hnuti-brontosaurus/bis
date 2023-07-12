import { useCurrentUser } from 'hooks/currentUser'
import { Navigate } from 'react-router-dom'

export const ViewMyProfile = () => {
  const { data: currentUser } = useCurrentUser()

  // only use this component when current user is already resolved in parent component
  return <Navigate to={`/profil/${currentUser!.id}`} replace />
}
