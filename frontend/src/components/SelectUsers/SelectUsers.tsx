import { yupResolver } from '@hookform/resolvers/yup'
import { FetchBaseQueryError, skipToken } from '@reduxjs/toolkit/query'
import { api } from 'app/services/bis'
import { User, UserSearch } from 'app/services/bisTypes'
import * as translations from 'config/static/translations'
import {
  Actions,
  BirthdayInput,
  birthdayValidation,
  FormInputError,
  LoadingIcon,
} from 'components'
import modalStyles from 'components/StyledModal/StyledModal.module.scss'
import { useDebouncedState } from 'hooks/debouncedState'
import { useReadUnknownAndFullUsers } from 'hooks/readUnknownAndFullUsers'
import { forwardRef, InputHTMLAttributes, ReactNode, useState } from 'react'
import { confirmAlert } from 'react-confirm-alert'
import {
  Controller,
  FormProvider,
  useForm,
  UseFormReturn,
} from 'react-hook-form'
import { FaBirthdayCake } from 'react-icons/fa'
import Select from 'react-select'
import { Assign } from 'utility-types'
import * as yup from 'yup'
import { Button } from '..'
import styles from './SelectUsers.module.scss'

type SelectObjectsProps<T> = Omit<
  Assign<
    InputHTMLAttributes<HTMLInputElement>,
    {
      value?: T[]
      onChange: (value: readonly T[]) => void
    }
  >,
  'defaultValue'
>
/**
 * This component expects - and provides - not only user ids, but array of full users as value
 */
export const SelectFullUsers = forwardRef<any, SelectObjectsProps<User>>(
  ({ value, onChange, ...rest }, ref) => {
    const [searchQuery, debouncedSearchQuery, setSearchQuery] =
      useDebouncedState(1000, '')
    const { data: userOptions, isLoading: isOptionsLoading } =
      api.endpoints.readUsers.useQuery(
        debouncedSearchQuery.length >= 2
          ? {
              search: debouncedSearchQuery,
            }
          : skipToken,
      )

    return (
      <Select
        {...rest}
        isLoading={isOptionsLoading}
        ref={ref}
        isMulti
        isClearable
        options={userOptions ? userOptions.results : []}
        inputValue={searchQuery}
        onInputChange={input => setSearchQuery(input)}
        value={value}
        onChange={onChange}
        getOptionLabel={user => user.display_name}
        getOptionValue={user => String(user.id)}
      />
    )
  },
)

export type SelectObjectProps<T, U = T> = Omit<
  Assign<
    InputHTMLAttributes<HTMLInputElement>,
    {
      value?: U
      onChange: (value: U | null) => void
      getDisabled?: (value: T) => string
      getLabel?: (value: T) => string
    }
  >,
  'defaultValue'
>

/**
 * This component expects - and provides - not only user id, but full user as value
 */
export const SelectFullUser = forwardRef<any, SelectObjectProps<User>>(
  ({ value, onChange, getDisabled, getLabel, ...rest }, ref) => {
    const [searchQuery, debouncedSearchQuery, setSearchQuery] =
      useDebouncedState(1000, '')
    const { data: userOptions, isLoading: isOptionsLoading } =
      api.endpoints.readUsers.useQuery(
        debouncedSearchQuery.length >= 2
          ? {
              search: debouncedSearchQuery,
            }
          : skipToken,
      )

    return (
      <Select<User>
        {...rest}
        isLoading={isOptionsLoading}
        ref={ref}
        isClearable
        options={userOptions ? userOptions.results : []}
        inputValue={searchQuery}
        onInputChange={input => setSearchQuery(input)}
        value={value}
        onChange={onChange}
        isOptionDisabled={user => Boolean(getDisabled?.(user))}
        getOptionLabel={getLabel ?? (user => user.display_name)}
      />
    )
  },
)

/**
 * This component searches in all users, and if current user doesn't have access, they have to provide birthdate
 */
export const SelectUnknownUser = forwardRef<
  any,
  SelectObjectProps<UserSearch | User, User> & {
    onBirthdayError?: (message: string) => void
  }
>(
  (
    { value, onChange, getDisabled, getLabel, onBirthdayError, ...rest },
    ref,
  ) => {
    const [searchQuery, debouncedSearchQuery, setSearchQuery] =
      useDebouncedState(1000, '')
    const {
      data: userOptions,
      isFetching: isOptionsFetching,
      isFullUsersFetching,
    } = useReadUnknownAndFullUsers(
      debouncedSearchQuery.length >= 2
        ? {
            search: debouncedSearchQuery,
          }
        : skipToken,
    )

    const readFullUser = useReadFullUser()

    return (
      <Select<UserSearch | User>
        {...rest}
        isLoading={searchQuery !== debouncedSearchQuery || isOptionsFetching}
        ref={ref}
        isClearable
        options={userOptions ? userOptions : []}
        inputValue={searchQuery}
        filterOption={() => true}
        onInputChange={input => setSearchQuery(input)}
        value={value}
        onChange={async user => {
          if (!user) return onChange(user)
          if ('id' in user) return onChange(user)
          try {
            const fullUser = await readFullUser(user)
            if (getDisabled && getDisabled(fullUser)) {
              throw new Error(getDisabled(fullUser))
            }
            return onChange(fullUser)
          } catch (error) {
            if (error instanceof Error && error.message === 'Canceled') return
            else if (error instanceof Error) onBirthdayError?.(error.message)
            else onBirthdayError?.('Jiná chyba')
          }
        }}
        isOptionDisabled={user =>
          Boolean(getDisabled?.(user)) ||
          (isFullUsersFetching && !('id' in user))
        }
        getOptionLabel={
          getLabel ?? (user => user.display_name + ('id' in user ? '' : ' ?'))
        }
        formatOptionLabel={user =>
          formatUnknownUserOptionLabel(user, isOptionsFetching, getLabel)
        }
        getOptionValue={user => user._search_id}
      />
    )
  },
)

const formatUnknownUserOptionLabel = (
  user: User | UserSearch,
  isLoading: boolean,
  getLabel?: (user: User | UserSearch) => string | ReactNode,
): ReactNode => (
  <div className={styles.optionLabel}>
    {getLabel ? getLabel(user) : user.display_name}
    {'id' in user ? null : isLoading ? <LoadingIcon /> : <FaBirthdayCake />}
  </div>
)

const birthdayValidationSchema: yup.ObjectSchema<{
  birthday: string
}> = yup.object({ birthday: birthdayValidation.required() })

export const BirthdayForm = ({
  onSubmit,
  onCancel,
}: {
  onSubmit: (
    data: { birthday: string },
    form: UseFormReturn<{ birthday: string }>,
  ) => Promise<void> | void
  onCancel: () => void
}) => {
  const methods = useForm<{ birthday: string }>({
    resolver: yupResolver(birthdayValidationSchema),
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { handleSubmit, control } = methods

  const handleFormSubmit = handleSubmit(async data => {
    if (isSubmitting) return
    setIsSubmitting(true)
    try {
      await onSubmit(data, methods)
    } finally {
      setIsSubmitting(false)
    }
  })

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleFormSubmit}
        onReset={e => {
          e.preventDefault()
          onCancel()
        }}
      >
        <FormInputError>
          <Controller
            control={control}
            name="birthday"
            render={({ field }) => <BirthdayInput {...field} />}
          />
        </FormInputError>
        <div className={styles.attemptsHint}>
          {translations.unknownUser.attempts_hint}
        </div>
        <Actions>
          <Button type="reset">Zrušit</Button>
          <Button
            primary
            type="submit"
            disabled={isSubmitting}
            isLoading={isSubmitting}
          >
            Pokračovat
          </Button>
        </Actions>
      </form>
    </FormProvider>
  )
}

/**
 * This component expects - and provides - not only user ids, but array of full users as value
 */
export const SelectUnknownUsers = forwardRef<
  any,
  SelectObjectsProps<User | UserSearch> & {
    onBirthdayError?: (message: string) => void
  }
>(({ value, onChange, onBirthdayError, ...rest }, ref) => {
  const [searchQuery, debouncedSearchQuery, setSearchQuery] = useDebouncedState(
    1000,
    '',
  )
  const {
    data: userOptions,
    isFetching: isOptionsFetching,
    isFullUsersFetching,
  } = useReadUnknownAndFullUsers(
    debouncedSearchQuery.length >= 2
      ? {
          search: debouncedSearchQuery,
        }
      : skipToken,
  )

  const readFullUser = useReadFullUser()

  return (
    <Select
      {...rest}
      isLoading={searchQuery !== debouncedSearchQuery || isOptionsFetching}
      ref={ref}
      isMulti
      isClearable={false}
      options={userOptions ?? []}
      inputValue={searchQuery}
      onInputChange={input => setSearchQuery(input)}
      value={value}
      onChange={async users => {
        // first, find the user without id (unknown)
        const userIndex = users.findIndex(user => !('id' in user))
        const user = users[userIndex]
        if (!user) return onChange([...users])

        try {
          const fullUser = await readFullUser(user)
          const updatedUsers = [...users] as User[]
          updatedUsers[userIndex] = fullUser
          return onChange(updatedUsers)
        } catch (e) {
          if (e instanceof Error && e.message === 'Canceled') return
          else if (e instanceof Error) onBirthdayError?.(e.message)
          else {
            onBirthdayError?.('Jiná chyba')
          }
        }
      }}
      getOptionLabel={user => user.display_name + ('id' in user ? '' : ' ?')}
      isOptionDisabled={user =>
        isFullUsersFetching && !('id' in (user as User | UserSearch))
      }
      getOptionValue={user => user._search_id}
      formatOptionLabel={user =>
        formatUnknownUserOptionLabel(user, isOptionsFetching)
      }
    />
  )
})

/**
 * Error thrown to callers of useReadFullUser when the user cancels the
 * birthday-verification dialog. Callers treat it as a silent no-op.
 */
const canceledError = new Error('Canceled')

const getVerificationErrorMessage = (
  error: FetchBaseQueryError,
): string | null => {
  switch (error.status) {
    case 404:
      // wrong birthday: let the user correct it in the dialog
      return translations.unknownUser.wrong_birthday
    case 429:
      // throttled: max 5 failures per (first_name, last_name, requester) per 24h
      return translations.unknownUser.locked_out
    default:
      return null
  }
}

export const useReadFullUser = () => {
  const [readUserByBirthday] = api.endpoints.readUserByBirthdate.useLazyQuery()
  return async (user: UserSearch): Promise<User> => {
    // settled once the dialog flow ends: a full user on success,
    // canceledError on cancel/escape/dismiss, or an Error with a message to
    // surface to the caller (fallback; normally errors stay in the dialog)
    let settle: (value: User | Error) => void = () => undefined
    const result = new Promise<User>((resolve, reject) => {
      settle = value =>
        value instanceof Error ? reject(value) : resolve(value)
    })

    // settle only once, no matter how many close paths fire
    let finish = (value: User | Error) => {
      settle(value)
      finish = () => undefined
    }

    confirmAlert({
      customUI: ({ title, message, onClose }) => {
        return (
          <div className={modalStyles.modal}>
            <div className={modalStyles.content}>
              <header className={modalStyles.modalTitleBox}>{title}</header>
              <div className={modalStyles.modalFormBox}>
                <div className={modalStyles.infoBox}>{message}</div>
                <BirthdayForm
                  onSubmit={async ({ birthday }, form) => {
                    try {
                      const fullUser = await readUserByBirthday({
                        ...user,
                        birthday,
                      }).unwrap()

                      if (fullUser._search_id === user._search_id) {
                        finish(fullUser)
                        onClose()
                      } else {
                        // verified user doesn't match the picked one
                        form.setError('birthday', {
                          type: 'manual',
                          message: translations.unknownUser.wrong_birthday,
                        })
                      }
                    } catch (error) {
                      if (
                        error &&
                        typeof error === 'object' &&
                        'status' in error
                      ) {
                        const verificationError = getVerificationErrorMessage(
                          error as FetchBaseQueryError,
                        )
                        if (verificationError) {
                          form.setError('birthday', {
                            type: 'manual',
                            message: verificationError,
                          })
                          return
                        }
                      }
                      form.setError('birthday', {
                        type: 'manual',
                        message: translations.unknownUser.verification_failed,
                      })
                    }
                  }}
                  onCancel={() => {
                    finish(canceledError)
                    onClose()
                  }}
                />
              </div>
            </div>
          </div>
        )
      },
      // the dialog can also be closed via Escape / click outside; treat
      // those like cancel (this also settles the promise on unmount)
      willUnmount: () => finish(canceledError),
      title: 'Zadat datum narození',
      message: user.display_name,
    })

    return result
  }
}
