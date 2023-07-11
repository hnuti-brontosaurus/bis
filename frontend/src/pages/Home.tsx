import { useCurrentUser } from 'hooks/currentUser'
import { useCurrentAccess } from 'hooks/useCurrentAccess'
import { Home as OrgHome } from 'org/pages/Home'
import { Home as UserHome } from 'user/pages/Home'

export const Home = () => {
  const { data: user } = useCurrentUser()
  const [access] = useCurrentAccess()
  if (!user) return null
  return access === 'organizer' ? (
    <OrgHome />
  ) : access === 'user' ? (
    <UserHome />
  ) : null
}
