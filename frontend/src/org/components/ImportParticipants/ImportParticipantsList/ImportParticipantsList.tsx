import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import { User, UserPayload } from 'app/services/bisTypes'
import classNames from 'classnames'
import { Actions, Button, LoadingIcon } from 'components'
import { UserForm, userValidationSchema } from 'components/UserForm/UserForm'
import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import { mergeWith, pick } from 'lodash'
import merge from 'lodash/merge'
import { useEffect, useMemo, useState } from 'react'
import { FaTimesCircle, FaUserCheck, FaUserPlus } from 'react-icons/fa'
import { formatDateTime } from 'utils/helpers'
import { UserImport } from '../ImportParticipants'
import { import2payload } from './helpers'
import styles from './ImportParticipantsList.module.scss'

const statusIcons = {
  pending: <LoadingIcon />,
  found: <FaUserCheck />,
  notFound: <FaUserPlus />,
  error: <FaTimesCircle />,
}

const statusTitles = {
  pending: '',
  found: 'Uživatel/ka existuje',
  notFound: 'Uživatel/ka bude vytvořen/a',
  error: 'Chyba',
}

type RequestStatus = ReturnType<typeof getRequestStatus>

type ProcessedUserWithStatus = {
  status: RequestStatus
  user: ConfirmedUser
  isValid: boolean | undefined
}

export type ConfirmedUser =
  | UserPayload
  | ({ id: string } & Partial<UserPayload>)

export const ImportParticipantsList = ({
  data: initialData = [],
  onConfirm,
  onCancel,
}: {
  data?: UserImport[]
  onConfirm: (data: ConfirmedUser[]) => Promise<void>
  onCancel: () => void
}) => {
  const [selectedRow, setSelectedRow] = useState<number>(-1)
  const [processedData, setProcessedData] = useState<ProcessedUserWithStatus[]>(
    [],
  )
  const [isSaving, setIsSaving] = useState(false)

  const showMessage = useShowMessage()

  const handleConfirm = () => {
    if (processedData.some(({ isValid }) => !isValid))
      return showMessage({
        message: 'Opravte, prosím, chyby ve validaci!',
        type: 'error',
      })

    setIsSaving(true)
    onConfirm(processedData.map(({ user }) => user)).finally(() => {
      setIsSaving(false)
    })
  }

  const handleUserDataChange = (
    row: number,
    processed: ProcessedUserWithStatus,
  ) => {
    setProcessedData(data => {
      if (data[row] === processed) return data
      const clonedData = [...data]
      clonedData[row] = processed
      return clonedData
    })
  }

  return (
    <div className={styles.container}>
      <table className={styles.table}>
        <thead>
          <tr>
            <td>Jméno</td>
            <td>Příjmení</td>
            <td>Datum narození</td>
            <td></td>
          </tr>
        </thead>
        <tbody>
          {initialData.map((userImport, i) => (
            <RowWithForm
              initialData={userImport}
              expanded={i === selectedRow}
              onToggle={() => setSelectedRow(row => (row === i ? -1 : i))}
              key={`${userImport.first_name}_${userImport.last_name}_${userImport.birthday}_${userImport.email}`}
              onChange={userWithState => handleUserDataChange(i, userWithState)}
            />
          ))}
        </tbody>
      </table>
      <Actions>
        <Button secondary onClick={onCancel}>
          Zrušit
        </Button>
        <Button primary isLoading={isSaving} onClick={handleConfirm}>
          Přidat do seznamu
        </Button>
      </Actions>
    </div>
  )
}

const getRequestStatus = (
  request: ReturnType<typeof api.endpoints.readUserByBirthdate.useQuery>,
) => {
  if (request.isLoading || request.isUninitialized) return 'pending'
  if (request.isSuccess) return 'found'
  if (
    request.error &&
    'status' in request.error &&
    request.error.status === 404
  )
    return 'notFound'

  return 'error'
}

const prepareUserForValidation = (user?: Partial<UserPayload>) =>
  mergeWith(
    {
      isChild: false,
      close_person: { first_name: '', last_name: '', email: '', phone: '' },
      contact_address: { street: '', city: '', zip_code: '' },
      health_insurance_company: 0,
      pronoun: 0,
      email: '',
    },
    user,
    (objValue, srcValue) => srcValue ?? objValue,
  )

const RowWithForm = ({
  initialData,
  expanded,
  onToggle,
  onChange,
}: {
  initialData: UserImport
  expanded: boolean
  onToggle: () => void
  onChange: (userWithState: ProcessedUserWithStatus) => void
}) => {
  const [searchUserParams, setSearchUserParams] = useState<{
    first_name?: string
    last_name?: string
    birthday?: string
  }>()

  const request = api.endpoints.readUserByBirthdate.useQuery(
    searchUserParams &&
      searchUserParams.first_name &&
      searchUserParams.last_name &&
      searchUserParams.birthday
      ? (searchUserParams as {
          first_name: string
          last_name: string
          birthday: string
        })
      : skipToken,
  )
  const { data: healthInsuranceCompanies } =
    api.endpoints.readHealthInsuranceCompanies.useQuery({})

  // here, we keep current user data
  const [currentData, setCurrentData] = useState<ConfirmedUser>()

  // here, we keep the current request status
  const [status, setStatus] = useState<RequestStatus>('pending')

  // keep track of the validity of the field
  const [isValid, setIsValid] = useState<boolean>()

  // validate currentData
  useEffect(() => {
    setIsValid(undefined)
    userValidationSchema
      .validate(prepareUserForValidation(currentData))
      .then(() => {
        setIsValid(true)
      })
      .catch(() => {
        setIsValid(false)
      })
  }, [currentData])

  // change status when request changes
  useEffect(() => {
    setStatus(getRequestStatus(request))
  }, [request])

  // return data when initial data are provided and when user is fetched
  useEffect(() => {
    const confirmed = import2payload(initialData, {
      healthInsuranceCompanies: healthInsuranceCompanies?.results ?? [],
      loaded: request.data,
    })
    setCurrentData(confirmed)
  }, [healthInsuranceCompanies?.results, initialData, request.data])

  const currentDataWithStatus: ProcessedUserWithStatus | undefined = useMemo(
    () => (currentData ? { status, user: currentData, isValid } : undefined),
    [currentData, isValid, status],
  )

  // when current data or status change, let the parent component know
  useEffect(() => {
    if (currentDataWithStatus) {
      onChange(currentDataWithStatus)
    }
  }, [currentData, currentDataWithStatus, onChange])

  const icon = statusIcons[status]
  const title =
    status === 'error' && request.error && 'message' in request.error
      ? 'Chyba ' + request.error.message
      : statusTitles[status]

  // data that are used to initialize form
  const initialFormData = useMemo(
    () =>
      merge({}, currentData, {
        health_insurance_company: currentData?.health_insurance_company
          ? { id: currentData.health_insurance_company }
          : undefined,
      }) as unknown as User,
    [currentData],
  )

  // change parameters for searching user when name or birthday changes
  useEffect(() => {
    setSearchUserParams(searchUserParams => {
      if (
        currentData &&
        (!searchUserParams ||
          !(
            searchUserParams.first_name === currentData?.first_name &&
            searchUserParams.last_name === currentData.last_name &&
            searchUserParams.birthday === currentData.birthday
          ))
      )
        return pick(currentData, 'first_name', 'last_name', 'birthday')
      else return searchUserParams
    })
  }, [currentData])

  if (!currentData) return null

  const handleFormSubmit = (user: UserPayload, id?: string) => {
    setCurrentData(merge(user, id ? { id } : undefined))
    onToggle()
  }

  return (
    <>
      <tr
        onClick={onToggle}
        className={classNames(
          styles.userRow,
          isValid === false && styles.invalid,
          isValid === undefined && styles.validating,
        )}
      >
        <td>{currentData.first_name}</td>
        <td>{currentData.last_name}</td>
        <td>
          {currentData.birthday ? formatDateTime(currentData.birthday) : null}
        </td>
        <td>
          <span title={title} aria-label={title}>
            {icon}
          </span>
        </td>
      </tr>
      {expanded && currentData && (
        <tr>
          <td colSpan={4}>
            <UserForm
              id={`${currentData.first_name}_
                ${currentData.last_name}_
                ${currentData.birthday}_
                ${currentData.email}`}
              initialData={initialFormData}
              validateImmediately
              onSubmit={handleFormSubmit}
              onCancel={onToggle}
            />
          </td>
        </tr>
      )}
    </>
  )
}
