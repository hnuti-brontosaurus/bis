import { ButtonLink, Error } from 'components'

export const NotFound = () => {
  return (
    <Error status={404} message="Tady nic není…">
      <div>
        Pokračovat na{' '}
        <ButtonLink tertiary to="/">
          hlavní stránku
        </ButtonLink>
      </div>
    </Error>
  )
}
