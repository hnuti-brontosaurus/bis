import { SerializedError } from '@reduxjs/toolkit'
import type { FetchBaseQueryError } from '@reduxjs/toolkit/query'
import { api } from 'app/services/bis'
import classNames from 'classnames'
import { Button, ButtonLink, FormInputError, Loading } from 'components'
import { useTitle } from 'hooks/title'
import styles from 'pages/Login/Login.module.scss'
import { ReactNode } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { required } from 'utils/validationMessages'

const getErrorMessage = (
  error: FetchBaseQueryError | SerializedError,
): ReactNode => {
  if ('status' in error) {
    if (error.status === 500) {
      return 'Problém s odesláním odkazu. Prosím zkuste to znovu.'
    } else if (error.status === 429) {
      return 'Příliš mnoho neúspěšných pokusů o přihlášení k vašemu účtu. Před opětovným odesláním odkazu musíte počkat 1 hodinu.'
    } else {
      return 'Problém s odesláním odkazu. Prosím zkuste to znovu.'
    }
  }
  return 'Problém s odesláním odkazu. Prosím zkuste to znovu.'
}

export const SendResetPasswordLink = () => {
  useTitle('Požádat o nastavení hesla')
  const [sendResetPasswordLink, { error, isLoading, isSuccess }] =
    api.endpoints.sendResetPasswordLink.useMutation()

  const formMethods = useForm<{ email: string }>()
  const { register, handleSubmit } = formMethods

  const handleFormSubmit = handleSubmit(async data => {
    await sendResetPasswordLink(data).unwrap()
  })

  if (isLoading) {
    return <Loading hideHeader>Zpracováváme požadavek</Loading>
  }

  if (isSuccess) {
    return (
      <div className={styles.loginContainer}>
        <div className={styles.formContainer}>
          <header className={styles.title}>Reset hesla</header>
          <p className={styles.subtitle}>
            Byla Ti zaslána e-mailová zpráva s pokyny, jak resetovat heslo.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.loginContainer}>
      <div className={styles.formContainer}>
        <header className={styles.title}>Reset hesla</header>
        <div>
          <ButtonLink tertiary to="/login">
            zpět
          </ButtonLink>
        </div>
        <p className={styles.subtitle}>
          Zadej svou e-mailovou adresu použitou při registraci.
          <br />
          Zašleme Ti e-mail s odkazem pro resetování hesla.
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
                className={classNames(styles.formElement)}
                type="text"
                placeholder="E-mail"
                {...register('email', {
                  required,
                  pattern: {
                    message: 'Zadejte email',
                    // https://stackoverflow.com/a/24980411 quite random regex
                    // TODO needs to be replaced with django-rest-framework version or something else better than this
                    value:
                      /^[^<>()[\]\\,;:%#^\s@"$&!@]+@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z0-9]+\.)+[a-zA-Z]{2,}))$/,
                  },
                })}
              />
            </FormInputError>
            <Button primary className={styles.formElement} type="submit">
              Obnovit
            </Button>
          </form>
        </FormProvider>
      </div>
    </div>
  )
}
