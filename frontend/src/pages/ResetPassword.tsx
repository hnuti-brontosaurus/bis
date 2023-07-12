import { SerializedError } from '@reduxjs/toolkit'
import { FetchBaseQueryError } from '@reduxjs/toolkit/query'
import { api } from 'app/services/bis'
import classNames from 'classnames'
import {
  Button,
  FormInputError,
  Loading,
  TogglePasswordInput,
} from 'components'
import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import { useTitle } from 'hooks/title'
import styles from 'pages/Login/Login.module.scss'
import { lazy, ReactNode, Suspense } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { Link, useSearchParams } from 'react-router-dom'

const PasswordStrengthBar = lazy(() => import('react-password-strength-bar'))

const getErrorMessage = (
  error: FetchBaseQueryError | SerializedError,
): ReactNode => {
  if ('status' in error) {
    if (error.status === 400) {
      if ('data' in error && Array.isArray(error.data)) {
        return (
          <>
            {error.data.map(a => (
              <div>
                {a}
                <br />
              </div>
            ))}
          </>
        )
      }
      return 'Zadejte silnější heslo.'
    } else if (error.status === 500) {
      return 'Byl problém se změnou hesla. Prosím zkuste to znovu.'
    } else if (error.status === 401) {
      return (
        <>
          Odkaz je chybný nebo propadlý.{' '}
          <Link className={styles.inlineLink} to="/send-reset-password-link">
            Poslat jiný
          </Link>
        </>
      )
    } else if (error.status === 429) {
      return 'Příliš mnoho neúspěšných pokusů o reset hesla. Před opětovným pokusem musíte počkat 1 hodinu.'
    }
  }
  return 'Nepodařilo se změnit heslo'
}

export const ResetPassword = () => {
  useTitle('Nastavit heslo')
  // use search parameters
  const [searchParams] = useSearchParams()
  const email = searchParams.get('email') ?? ''
  const code = searchParams.get('code') ?? ''
  const [resetPassword, { isLoading, error }] =
    api.endpoints.resetPassword.useMutation()
  const showMessage = useShowMessage()

  const formMethods = useForm<{ password: string; passwordRepeat: string }>()

  const { register, handleSubmit, getValues, watch } = formMethods
  const handleFormSubmit = handleSubmit(async data => {
    await resetPassword({
      password: data.password,
      email,
      code,
    }).unwrap()

    showMessage({
      type: 'success',
      message: 'Heslo bylo aktualizováno',
      detail: 'Paráda! Nastavil/a sis nové heslo a jsi už přihlášen/a.',
    })
  })

  if (!(email && code)) {
    return (
      <div className={styles.loginContainer}>
        <div className={styles.formContainer}>
          <header className={styles.title}>Neplatná adresa</header>
          <p className={styles.subtitle}>
            Vypadá to, že jste tuto stránku neotevřeli z emailu.
            <br />
            Chtěli jste{' '}
            <Link className={styles.inlineLink} to="/send-reset-password-link">
              obnovit heslo?
            </Link>
          </p>
        </div>
      </div>
    )
  }

  if (isLoading) return <Loading hideHeader>Zpracováváme požadavek</Loading>

  return (
    <div className={styles.loginContainer}>
      <div className={styles.formContainer}>
        <header className={styles.title}>Resetovat heslo</header>
        {error && (
          <div className={classNames(styles.error, styles.formElement)}>
            {getErrorMessage(error)}
          </div>
        )}
        <FormProvider {...formMethods}>
          <form onSubmit={handleFormSubmit}>
            <FormInputError name="password" isBlock>
              <>
                <TogglePasswordInput
                  className={styles.formElement}
                  placeholder="nové heslo"
                  {...register('password', {
                    required: 'Zadej, prosím, své heslo',
                  })}
                />
                <Suspense>
                  {watch('password') && (
                    <PasswordStrengthBar
                      password={watch('password')}
                      className={styles.passwordStrengthBar}
                      scoreWords={[
                        'velmi slabé',
                        'slabé',
                        'nepříliš dobré',
                        'dobré',
                        'skvělé',
                      ]}
                      barColors={[
                        '#d9d9d9',
                        '#ff1616',
                        '#ffde59',
                        '#00a340',
                        '#008037',
                      ]}
                      minLength={8}
                      shortScoreWord="příliš krátké"
                    />
                  )}
                </Suspense>
              </>
            </FormInputError>
            <FormInputError isBlock>
              <TogglePasswordInput
                className={styles.formElement}
                placeholder="zopakuj nové heslo"
                {...register('passwordRepeat', {
                  validate: pwd =>
                    getValues('password') === pwd || 'Ověř, prosím, své heslo',
                })}
              />
            </FormInputError>
            <Button primary className={styles.formElement} type="submit">
              Nastavit heslo
            </Button>
          </form>
        </FormProvider>
      </div>
    </div>
  )
}
