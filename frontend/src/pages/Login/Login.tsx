import type { SerializedError } from '@reduxjs/toolkit'
import type { FetchBaseQueryError } from '@reduxjs/toolkit/query'
import { api } from 'app/services/bis'
import classNames from 'classnames'
import {
  Button,
  ButtonLink,
  FormInputError,
  Loading,
  TogglePasswordInput,
} from 'components'
import { useTitle } from 'hooks/title'
import { FormProvider, useForm } from 'react-hook-form'
import { required } from 'utils/validationMessages'
import styles from './Login.module.scss'

const getErrorMessage = (
  error: FetchBaseQueryError | SerializedError,
): string => {
  if ('status' in error) {
    if (error.status === 400 || error.status === 401)
      return 'Problém s vaším přihlášením, zadejte prosím správné uživatelské jméno a heslo.'
    else if (error.status === 500) {
      return 'Byl problém s přihlášením. Prosím zkuste to znovu.'
    } else if (error.status === 429) {
      return 'Příliš mnoho neúspěšných pokusů o přihlášení k vašemu účtu. Před opětovným přihlášením musíte počkat 1 hodinu.'
    }
  }
  return 'Nepodařilo se přihlásit'
}

export const Login = () => {
  useTitle('Přihlášení do Brontosauřího Informačního Systému')
  const [login, { isLoading: isLoginLoading, error }] =
    api.endpoints.login.useMutation()

  const formMethods = useForm<{ email: string; password: string }>()
  const { register, handleSubmit } = formMethods

  const handleFormSubmit = handleSubmit(data => {
    login(data)
    // AuthenticatedOutlet should take care of the rest...
  })

  if (isLoginLoading)
    return <Loading hideHeader>Přihlášení do panelu Brontosaurus...</Loading>

  return (
    <div className={styles.loginContainer}>
      <div className={styles.formContainer}>
        <header className={styles.title}>Přihlaste se ke svému účtu</header>
        <p className={styles.subtitle}>
          Zadejte své přihlašovací jméno a heslo <br />
          pro přístup k aplikaci
        </p>
        {error && (
          <div className={classNames(styles.error, styles.formElement)}>
            {getErrorMessage(error)}
          </div>
        )}
        <FormProvider {...formMethods}>
          <form onSubmit={handleFormSubmit}>
            <FormInputError isBlock>
              <input
                className={styles.formElement}
                type="text"
                placeholder="E-mail"
                {...register('email', {
                  required,
                })}
              />
            </FormInputError>
            <FormInputError isBlock>
              <TogglePasswordInput
                className={styles.formElement}
                placeholder="Heslo"
                {...register('password', { required })}
              />
            </FormInputError>
            <Button primary className={styles.formElement} type="submit">
              Přihlásit se
            </Button>

            <ButtonLink
              tertiary
              style={{ marginTop: '1.5rem' }}
              className={styles.formElement}
              to="/send-reset-password-link"
            >
              přihlašuji se poprvé/zapomněl(a) jsem heslo
            </ButtonLink>
            <div className={styles.help}>
              V případě problémů s přihlášením se obracej na{' '}
              <a href="mailto:bis@brontosaurus.cz">bis@brontosaurus.cz</a>
            </div>
          </form>
        </FormProvider>
      </div>
    </div>
  )
}
