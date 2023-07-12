import { Error, Loading } from 'components'
import { useCurrentUser } from 'hooks/currentUser'
import { Outlet } from 'react-router-dom'
import { hasUserOrganizerAccess } from 'utils/roles'

export const OrganizerOutlet = () => {
  const { data: user, isLoading } = useCurrentUser()

  if (isLoading) return <Loading>Ověřujeme Tvé role</Loading>
  if (!user) return <div>This is error, You're a ghost</div>

  return hasUserOrganizerAccess(user) ? (
    <Outlet />
  ) : (
    <Error
      status={403}
      message="Nemáš dostatečná práva k organizátorskému přístupu"
    >
      Pro vstup do organizátorského přístupu Brontosauřího informačního systému
      BIS nemáš dostatečná oprávnění. Pokud i přesto chceš zadat do BISu akci,
      napiš na <a href="mailto:bis@brontosaurus.cz">bis@brontosaurus.cz</a>.
      <br />
      Hnutí Brontosaurus
    </Error>
  )
}
