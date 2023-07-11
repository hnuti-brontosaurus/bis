import { ButtonLink, Error, Loading } from 'components'
import { useCurrentUser } from 'hooks/currentUser'
import { Outlet } from 'react-router-dom'
import { hasUserAdminAccess } from 'utils/roles'

export const AdminOutlet = () => {
  const { data: user, isLoading } = useCurrentUser()

  if (isLoading) return <Loading>Ověřujeme Tvé role</Loading>
  if (!user) return <Error message="Nejsi přihlášen/a" />

  return hasUserAdminAccess(user) ? (
    <Outlet />
  ) : (
    <Error
      status={403}
      message="Nemáš dostatečná práva k administrátorskému přístupu"
    >
      <div>
        <p>
          Pro vstup do administrátorského přístupu Brontosauřího informačního
          systému BIS nemáš dostatečná oprávnění. Pokud i přesto potřebuješ
          udělat něco administrátorského, napiš na{' '}
          <a href="mailto:bis@brontosaurus.cz">bis@brontosaurus.cz</a>.
        </p>
        <p>Hnutí Brontosaurus</p>
      </div>
      <div>
        Pokračuj na{' '}
        <ButtonLink tertiary to="/">
          domácí stránku
        </ButtonLink>
      </div>
    </Error>
  )
}
