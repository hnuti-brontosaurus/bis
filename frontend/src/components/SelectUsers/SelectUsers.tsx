import { yupResolver } from '@hookform/resolvers/yup'
import { FetchBaseQueryError, skipToken } from '@reduxjs/toolkit/query'
import { api } from 'app/services/bis'
import { User, UserSearch } from 'app/services/bisTypes'
import {
  Actions,
  BirthdayInput,
  birthdayValidation,
  FormInputError,
  LoadingIcon,
} from 'components'
import { useDebouncedState } from 'hooks/debouncedState'
import { useReadUnknownAndFullUsers } from 'hooks/readUnknownAndFullUsers'
import { forwardRef, InputHTMLAttributes, ReactNode } from 'react'
import { Controller, FormProvider, useForm } from 'react-hook-form'
import { FaBirthdayCake } from 'react-icons/fa'
import Select from 'react-select'
import { Assign } from 'utility-types'
import { openModal } from 'utils/openModal'
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
    const { data: userOptions, isFetching: isOptionsFetching } =
      useReadUnknownAndFullUsers(
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
            if (!fullUser) return
            if (getDisabled && getDisabled(fullUser)) {
              throw new Error(getDisabled(fullUser))
            }
            return onChange(fullUser)
          } catch (error) {
            if (error instanceof Error) onBirthdayError?.(error.message)
            else onBirthdayError?.('Jiná chyba')
          }
        }}
        isOptionDisabled={user => Boolean(getDisabled?.(user))}
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

/**
 * `onSubmit` throws an Error whose message is shown under the birthday input.
 */
export const BirthdayForm = ({
  onSubmit,
  onCancel,
}: {
  onSubmit: (data: { birthday: string }) => Promise<void>
  onCancel: () => void
}) => {
  const methods = useForm<{ birthday: string }>({
    resolver: yupResolver(birthdayValidationSchema),
  })
  const {
    handleSubmit,
    control,
    setError,
    formState: { isSubmitting },
  } = methods

  const handleFormSubmit = handleSubmit(async data => {
    try {
      await onSubmit(data)
    } catch (error) {
      if (!(error instanceof Error)) throw error
      setError('birthday', { type: 'manual', message: error.message })
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
          Po 5 neúspěšných pokusech se ověření na 24 hodin zablokuje.
        </div>
        <Actions>
          <Button type="reset">Zrušit</Button>
          <Button primary type="submit" isLoading={isSubmitting}>
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
  const { data: userOptions, isFetching: isOptionsFetching } =
    useReadUnknownAndFullUsers(
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
          if (!fullUser) return
          const updatedUsers = [...users] as User[]
          updatedUsers[userIndex] = fullUser
          return onChange(updatedUsers)
        } catch (e) {
          if (e instanceof Error) onBirthdayError?.(e.message)
          else {
            onBirthdayError?.('Jiná chyba')
          }
        }
      }}
      getOptionLabel={user => user.display_name + ('id' in user ? '' : ' ?')}
      getOptionValue={user => user._search_id}
      formatOptionLabel={user =>
        formatUnknownUserOptionLabel(user, isOptionsFetching)
      }
    />
  )
})

const getVerificationErrorMessage = (error: unknown) => {
  const status = (error as FetchBaseQueryError).status
  if (status === 404) return 'Nesprávné datum narození'
  // the backend allows 5 failures per name and requester in 24 hours
  if (status === 429)
    return 'Příliš mnoho neúspěšných pokusů. Ověření tohoto uživatele je na 24 hodin zablokováno.'
  return 'Ověření se nezdařilo. Zkus to prosím znovu.'
}

/**
 * Resolves with the full profile of the picked user, asking for their
 * birthday when the requester may not see them, or with null when the
 * birthday dialog is cancelled.
 */
export const useReadFullUser = () => {
  const [readUsers] = api.endpoints.readUsers.useLazyQuery()
  const [readUserByBirthday] = api.endpoints.readUserByBirthdate.useLazyQuery()

  const verifyBirthday = async (user: UserSearch, birthday: string) => {
    let verifiedUser: User
    try {
      verifiedUser = await readUserByBirthday({ ...user, birthday }).unwrap()
    } catch (error) {
      throw new Error(getVerificationErrorMessage(error))
    }
    if (verifiedUser._search_id !== user._search_id)
      throw new Error('Nesprávné datum narození')
    return verifiedUser
  }

  return async (user: UserSearch): Promise<User | null> => {
    // The option list fills in full profiles only once a slow query finishes,
    // so a user the requester may see can still be picked as unknown
    const { results: visibleUsers } = await readUsers(
      { _search_id: [user._search_id] },
      true,
    ).unwrap()
    if (visibleUsers.length > 0) return visibleUsers[0]

    return openModal<User>({
      title: 'Zadat datum narození',
      message: user.display_name,
      render: close => (
        <BirthdayForm
          onSubmit={async ({ birthday }) =>
            close(await verifyBirthday(user, birthday))
          }
          onCancel={() => close(null)}
        />
      ),
    })
  }
}
