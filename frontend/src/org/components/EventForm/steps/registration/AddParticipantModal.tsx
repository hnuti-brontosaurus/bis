import { yupResolver } from '@hookform/resolvers/yup'
import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import {
  EventApplication,
  User,
  UserPayload,
  UserSearch,
} from 'app/services/bisTypes'
import classNames from 'classnames'
import { Button, Loading, StyledModal } from 'components'
import { useReadFullUser } from 'components/SelectUsers/SelectUsers'
import stylesTable from 'components/Table.module.scss'
import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import { FC, Fragment, useState } from 'react'
import { useForm } from 'react-hook-form'
import { FaAt, FaBirthdayCake, FaPhoneAlt } from 'react-icons/fa'
import { IoIosArrowDown, IoIosArrowUp } from 'react-icons/io'
import Tooltip from 'react-tooltip-lite'
import colors from 'styles/colors.module.scss'
import * as yup from 'yup'
import { ApplicationStates } from '../ParticipantsStep'
import styles from './NewApplicationModal.module.scss'

interface INewApplicationModalProps {
  open: boolean
  onClose: () => void
  currentApplication: EventApplication
  eventId: number
  eventParticipants: string[]
  defaultUserData: EventApplication
  openAddNewUser: () => void
}

const zipcodeRegExp = /\d{3} ?\d{2}/

const validationSchema = yup.object().shape(
  {
    first_name: yup.string().required().trim(),
    last_name: yup.string().required(),
    nickname: yup.string().trim(),
    email: yup.string().email().required('email or phone is required'),
    phone: yup.string().required(),
    birthday: yup
      .date()
      .required()
      .transform((curr, orig) => (orig === '' ? null : curr)),
    close_person: yup.object().shape({
      first_name: yup.string().required(),
      last_name: yup.string().required(),
      email: yup.string().email().required('email or phone is required'),
      phone: yup.string().required(),
    }),
    address: yup.object().shape({
      street: yup.string().required(),
      city: yup.string().required(),
      zip_code: yup.string().required().matches(zipcodeRegExp),
    }),
  },
  [['email', 'phone']],
)

// TODO: This modal is still WIP (no need to review atm)
export const AddParticipantModal: FC<INewApplicationModalProps> = ({
  open,
  onClose,
  currentApplication,
  eventId,
  eventParticipants,
  defaultUserData,
  openAddNewUser,
}) => {
  const methods = useForm<UserPayload>({
    resolver: yupResolver(validationSchema),
  })

  const [showAddParticipantForm, setShowAddParticipantForm] = useState(false)

  const [erroredSearchId, setErroredSearchId] = useState<string>()

  const [selectedUser, setSelectedUser] = useState<User>()

  const [, /* creatingANewUser */ setCreatingANewUser] = useState(false)
  const [retrievedUserIsUsed, setRetrievedUserIsUsed] = useState(false)

  const showMessage = useShowMessage()

  const [selectedUserId, setSelectedUserId] = useState<string>('')
  const [selectedUserInputBirthday, setSelectedUserInputBirthday] = useState<{
    first_name: string
    last_name: string
    birthday: string
  }>({ first_name: '', last_name: '', birthday: '' })

  const { data: categories } = api.endpoints.readEventCategories.useQuery()
  const { data: administrationUnits } =
    api.endpoints.readAdministrationUnits.useQuery({ pageSize: 2000 })

  const { reset } = methods

  const { data: userOptions1, isFetching: isOptionsLoading1 } =
    api.endpoints.readUsers.useQuery({
      search: `${defaultUserData.first_name} ${defaultUserData.last_name}`,
    })

  const { data: userOptions2, isFetching: isOptionsLoading2 } =
    api.endpoints.readUsers.useQuery({
      search: `${defaultUserData.email?.split('@')[0]}`,
    })

  const { data: userOptions3, isFetching: isOptionsLoading3 } =
    api.endpoints.readUsers.useQuery(
      defaultUserData && defaultUserData.nickname
        ? {
            search: `${defaultUserData.nickname}`,
          }
        : skipToken,
    )

  const userOptionsDuplicates = [
    ...(userOptions1 ? userOptions1.results : []),
    ...(userOptions2 ? userOptions2.results : []),
    ...(userOptions3 ? userOptions3.results : []),
  ]

  const userOptions = Array.from(
    new Map(userOptionsDuplicates.map(item => [item['id'], item])).values(),
  )

  const userOptionsSearchIds = new Set(userOptions.map(u => u._search_id))

  const isOptionsLoading =
    isOptionsLoading1 || isOptionsLoading2 || isOptionsLoading3

  const { data: allUsersData, isFetching: isAllUsersLoading } =
    api.endpoints.readAllUsers.useQuery({
      search: `${defaultUserData.first_name} ${defaultUserData.last_name}`,
    })

  const allUsersDuplicates = allUsersData?.results ? allUsersData.results : []

  const allUsers = allUsersDuplicates.filter(
    u => !userOptionsSearchIds.has(u._search_id),
  )

  const isTheSameEmail = (
    email: string | null | undefined,
    emailsList: (string | null | undefined)[],
  ) => {
    if (!email || !emailsList) return false
    const filteredEmails = emailsList.filter(e => e && e === email)
    return filteredEmails.length >= 1
  }

  // const { data: retrievedUser, error: inlineUserError } =
  const { data: retrievedUser } = api.endpoints.readUserByBirthdate.useQuery(
    selectedUserInputBirthday &&
      selectedUserInputBirthday.birthday.length === 10
      ? selectedUserInputBirthday
      : skipToken,
  )
  const [patchEvent] = api.endpoints.updateEvent.useMutation()
  const readFullUser = useReadFullUser()

  const [updateApplication] = api.endpoints.updateEventApplication.useMutation()
  const addParticipant = async (newParticipantId: string) => {
    let newParticipants = [...eventParticipants]
    newParticipants.push(newParticipantId)

    await patchEvent({
      id: eventId,
      event: {
        record: {
          participants: newParticipants,
          contacts: [],
          number_of_participants: null,
          number_of_participants_under_26: null,
        },
      },
    })
  }

  const clearModalData = () => {
    setShowAddParticipantForm(false)
    setSelectedUser(undefined)
    setCreatingANewUser(false)
    setSelectedUserId('')
    setSelectedUserInputBirthday({
      first_name: '',
      last_name: '',
      birthday: '',
    })
    setErroredSearchId(undefined)
    setRetrievedUserIsUsed(false)
  }
  if (!open) return null

  const UserCollapseRow = ({ user }: { user: User }) => {
    return (
      <Fragment key={user.id}>
        <tr
          className={classNames(styles.myUsers, styles.collapseUserRow)}
          onClick={e => {
            e.preventDefault()

            if (user._search_id === selectedUserId) {
              setSelectedUserId('')

              // setCreatingANewUser(false)
              // setSelectedUser(undefined)

              return
            }
            setCreatingANewUser(false)
            setSelectedUser(user)
            reset(
              // TODO: fix pronoun type
              selectedUser as unknown as UserPayload,
            )
            setShowAddParticipantForm(true)
            setSelectedUserId(user._search_id)
            setShowAddParticipantForm(false)
          }}
        >
          <td>
            {user._search_id === selectedUserId ? (
              <IoIosArrowUp />
            ) : (
              <IoIosArrowDown />
            )}
          </td>
          <td className={styles.displayName}>
            <div>{user.display_name}</div>
          </td>
          <td>
            <Tooltip
              useDefaultStyles
              hoverDelay={
                currentApplication.birthday &&
                user.birthday &&
                currentApplication.birthday !== user.birthday
                  ? 0
                  : 10000
              }
              content={`${currentApplication.birthday}/${user.birthday}`}
            >
              <FaBirthdayCake
                color={
                  currentApplication.birthday && user.birthday
                    ? currentApplication.birthday === user.birthday
                      ? colors.bronto
                      : colors.error
                    : colors.gray300
                }
              />
            </Tooltip>
          </td>

          <td>
            <Tooltip
              useDefaultStyles
              hoverDelay={
                isTheSameEmail(currentApplication.email, [
                  ...user.all_emails,
                  user.email,
                ])
                  ? 0
                  : 10000
              }
              content={`${currentApplication.email}/${user.email}`}
            >
              <FaAt
                color={
                  currentApplication.email &&
                  (user.email ||
                    (user.all_emails && user.all_emails.length >= 1))
                    ? isTheSameEmail(currentApplication.email, [
                        ...user.all_emails,
                        user.email,
                      ])
                      ? colors.bronto
                      : colors.error
                    : colors.gray300
                }
              />
            </Tooltip>
          </td>
          <td>
            <Tooltip
              useDefaultStyles
              hoverDelay={
                currentApplication.phone &&
                user.phone &&
                currentApplication.phone !== user.phone
                  ? 0
                  : 10000
              }
              content={`${currentApplication.phone}/${user.phone}`}
            >
              <FaPhoneAlt
                color={
                  currentApplication.phone && user.phone
                    ? currentApplication.phone === user.phone
                      ? colors.bronto
                      : colors.error
                    : colors.gray300
                }
              />
            </Tooltip>
          </td>
          {/* <td>
            <Button
              secondary
              onClick={e => {
                e.preventDefault()

                setCreatingANewUser(false)
                setSelectedUser(user)
                reset(
                  // TODO: fix pronoun type
                  selectedUser as unknown as UserPayload,
                )
                setShowAddParticipantForm(true)
                setSelectedUserId(user._search_id)
                setShowAddParticipantForm(false)
              }}
            >
              Ukaž
            </Button>
          </td> */}
          <td>
            {!eventParticipants.includes(user.id) ? (
              <Button
                primary
                isLoading={
                  retrievedUser && user._search_id === retrievedUser._search_id
                }
                onClick={async e => {
                  e.preventDefault()
                  e.stopPropagation()

                  setCreatingANewUser(false)

                  await addParticipant(user.id)

                  await updateApplication({
                    id: currentApplication.id,
                    eventId: eventId,
                    patchedEventApplication: {
                      user: user.id,
                      state: ApplicationStates.approved,
                    },
                  })
                  onClose()
                  clearModalData()
                }}
              >
                {'Přidej'}
              </Button>
            ) : (
              <>
                <div className={styles.smallUserDuplicateText}>
                  Tento uživatel již byl přidán na seznam účastníků. Pokud se
                  jedná o jeho další přihlášku,{' '}
                  <Button
                    tertiary
                    small
                    className={styles.smallUserDuplicateButton}
                    isLoading={
                      retrievedUser &&
                      user._search_id === retrievedUser._search_id
                    }
                    onClick={async e => {
                      e.preventDefault()
                      e.stopPropagation()

                      setCreatingANewUser(false)

                      await addParticipant(user.id)

                      await updateApplication({
                        id: currentApplication.id,
                        eventId: eventId,
                        patchedEventApplication: {
                          user: user.id,
                          state: ApplicationStates.approved,
                        },
                      })
                      onClose()
                      clearModalData()
                    }}
                  >
                    spojte ji s tímto účastníkem.
                  </Button>
                </div>
              </>
            )}
          </td>
        </tr>
        {user._search_id === selectedUserId && (
          <tr>
            <td colSpan={6}>
              <>
                <span>Uživatel/ka: </span>
                <span>
                  {user.first_name} {user.last_name}{' '}
                  {user.nickname && `(${user.nickname})`}{' '}
                </span>
                {user.birthday && (
                  <div>
                    <span>Datum narození: </span>
                    <span>{user.birthday}</span>
                  </div>
                )}
                {user.pronoun?.name && (
                  <div>
                    <span>Oslovení: </span>
                    <span>{user.pronoun.name}</span>
                  </div>
                )}
                {user.email && (
                  <div>
                    <span>E-mail: </span>
                    <span>{user.email}</span>
                  </div>
                )}
                {user.phone && (
                  <div>
                    <span>Telefon: </span>
                    <span>{user.phone}</span>
                  </div>
                )}

                {user.health_issues && (
                  <div>
                    <span>Zdravotní omezení: </span>
                    <span>{user.health_issues}</span>
                  </div>
                )}
                {user.close_person && (
                  <div>
                    <span>Blízká osoba: </span>
                    <span>{`${user.close_person.first_name} ${user.close_person.last_name}`}</span>
                    {user.close_person.email && (
                      <span>{` email: ${user.close_person.email}`}</span>
                    )}
                    {user.close_person.phone && (
                      <span>{` tel: ${user.close_person.phone}`}</span>
                    )}
                  </div>
                )}
              </>
            </td>
          </tr>
        )}
      </Fragment>
    )
  }

  const UserWithoutAccessCollapseRow = ({ user }: { user: UserSearch }) => {
    return (
      <>
        <tr
          className={classNames(
            styles.otherUsers,
            erroredSearchId === user._search_id && styles.errorBirthdate,
            retrievedUser &&
              retrievedUserIsUsed &&
              retrievedUser._search_id === user._search_id &&
              styles.successBirthdate,
          )}
        >
          <td></td>

          <td>{user.display_name}</td>
          <td></td>
          <td></td>
          <td></td>
          <td colSpan={2}>
            <Button
              primary
              small
              onClick={async () => {
                try {
                  const fullUser = await readFullUser(user)
                  // const updatedUsers = [...users] as User[]
                  // updatedUsers[userIndex] = fullUser
                  // return onChange(updatedUsers)

                  if (fullUser && fullUser._search_id === user._search_id) {
                    addParticipant(fullUser.id)

                    await updateApplication({
                      id: currentApplication.id,
                      eventId: eventId,
                      patchedEventApplication: {
                        user: fullUser.id,
                        state: ApplicationStates.approved,
                      },
                    })
                    clearModalData()
                    onClose()
                  }
                } catch (e) {
                  const onBirthdayError = (message: string) => {
                    showMessage({
                      type: 'error',
                      message: 'Nepodařilo se přidat uživatele',
                      detail: message,
                    })
                  }
                  if (e instanceof Error && e.message === 'Canceled') return
                  else if (e instanceof Error) onBirthdayError?.(e.message)
                  else {
                    onBirthdayError?.('Jiná chyba')
                  }
                }
              }}
            >
              Pridaj
            </Button>
            {/* <div
              onClick={e => {
                e.stopPropagation()
              }}
            >
              <BirthdayInputCheck
                defaultBirthday={currentApplication.birthday}
                onSubmitBD={onSubmitBD}
                result={user}
                erroredSearchId={erroredSearchId}
                inlineUserError={inlineUserError}
                retrievedUser={retrievedUser}
                retrievedUserIsUsed={retrievedUserIsUsed}
                setCheckAndAdd={v => {
                  setCheckAndAdd(v)
                }}
              />
            </div> */}
          </td>
        </tr>
        {user._search_id === selectedUserId &&
          retrievedUser &&
          retrievedUser._search_id === user._search_id &&
          retrievedUserIsUsed && (
            <tr>
              <td colSpan={6}>
                <>
                  <span>Uživatel/ka: </span>
                  <span>
                    {retrievedUser.first_name} {retrievedUser.last_name}{' '}
                    {retrievedUser.nickname && `(${retrievedUser.nickname})`}{' '}
                  </span>
                  {retrievedUser.birthday && (
                    <div>
                      <span>Datum narození: </span>
                      <span>{retrievedUser.birthday}</span>
                    </div>
                  )}
                  {retrievedUser.memberships && (
                    <div>
                      <span>Členství: </span>
                      <span>
                        {retrievedUser.memberships.map(membership => {
                          return (
                            <>
                              {administrationUnits && categories && (
                                <div>
                                  <>
                                    <span>
                                      {
                                        administrationUnits.results.find(
                                          // @ts-ignore
                                          unit =>
                                            // @ts-ignore
                                            membership.administration_unit ===
                                            // @ts-ignore
                                            unit.id,
                                        )?.name
                                      }
                                    </span>
                                    <span>
                                      {
                                        categories.results.find(
                                          // @ts-ignore
                                          category =>
                                            // @ts-ignore
                                            membership.category ===
                                            // @ts-ignore
                                            category.id,
                                        )?.name
                                      }
                                    </span>
                                    <span>{' od: '}</span>
                                    <span>{membership.year}</span>
                                  </>
                                </div>
                              )}
                            </>
                          )
                        })}
                      </span>
                    </div>
                  )}
                  {retrievedUser.pronoun?.name && (
                    <div>
                      <span>Oslovení: </span>
                      <span>{retrievedUser.pronoun.name}</span>
                    </div>
                  )}
                  {retrievedUser.email && (
                    <div>
                      <span>E-mail: </span>
                      <span>{retrievedUser.email}</span>
                    </div>
                  )}
                  {retrievedUser.phone && (
                    <div>
                      <span>Telefon: </span>
                      <span>{retrievedUser.phone}</span>
                    </div>
                  )}
                  {/* {retrievedUser.address.street && (
<div>
<span>Adresa: </span>
<span>{`${retrievedUser.address.street || ''} ${
retrievedUser.address.city || ''
} ${retrievedUser.address.zip_code || ''} ${
retrievedUser.address.region || ''
}`}</span>
</div>
)} */}
                  {retrievedUser.health_issues && (
                    <div>
                      <span>Zdravotní omezení: </span>
                      <span>{retrievedUser.health_issues}</span>
                    </div>
                  )}
                  {retrievedUser.close_person && (
                    <div>
                      <span>Blízká osoba: </span>
                      <span>{`${retrievedUser.close_person.first_name} ${retrievedUser.close_person.last_name}`}</span>
                      {retrievedUser.close_person.email && (
                        <span>{` email: ${retrievedUser.close_person.email}`}</span>
                      )}
                      {retrievedUser.close_person.phone && (
                        <span>{` tel: ${retrievedUser.close_person.phone}`}</span>
                      )}
                    </div>
                  )}
                </>
              </td>
            </tr>
          )}
      </>
    )
  }

  return (
    <StyledModal
      open={open}
      onClose={() => {
        onClose()
        clearModalData()
      }}
      title="Přidání účastníka"
    >
      <div
        onClick={e => {
          e.stopPropagation()
        }}
        className={styles.addParticipantModal}
      >
        {userOptions.length === 0 && allUsers.length === 0 ? (
          <div className={styles.infoBox}>
            Podle data z přihlášky jsme nenašli žádné uživatele, kteří už mají
            svůj účet v BISu.{' '}
          </div>
        ) : (
          <div className={styles.infoBox}>
            Podle data z přihlášky jsme našli následující uživatele, kteří už
            mají svůj účet v BISu:{' '}
            <p>Zelení - uživatelé, ke kterým máš přístup</p>
            <p>
              Šedí - uživatelé, ke kterým nemáš přístup; a musíš zadat datum
              narození, abys je mohl(a) přidat jako účastníky
            </p>
          </div>
        )}

        <div>
          <div
            onClick={e => {
              e.stopPropagation()
            }}
          >
            <div className={styles.usersList}>
              {!(isOptionsLoading || isAllUsersLoading) ? (
                <table className={classNames(stylesTable.table, styles.table)}>
                  <tbody>
                    {(userOptions.length !== 0 || allUsers.length !== 0) && (
                      <tr>
                        <td colSpan={4}>
                          {' '}
                          <h3>Uživatelé přítomní v BISu</h3>{' '}
                        </td>
                        <td colSpan={2} style={{ textAlign: 'end' }}>
                          <span>
                            Ucastnik neni v BISu?{' '}
                            <Button
                              secondary
                              small
                              onClick={() => {
                                openAddNewUser()
                              }}
                            >
                              Přidej nového uživatele
                            </Button>
                          </span>
                        </td>
                      </tr>
                    )}
                    {!showAddParticipantForm &&
                      userOptions.length !== 0 &&
                      userOptions?.map(user => <UserCollapseRow user={user} />)}
                    {!showAddParticipantForm &&
                      allUsers.length !== 0 &&
                      allUsers.map(user => (
                        <UserWithoutAccessCollapseRow user={user} />
                      ))}
                  </tbody>
                </table>
              ) : (
                <Loading>Hledáme existující uživatele</Loading>
              )}
              {userOptions.length === 0 && allUsers.length === 0 && (
                <span>
                  Ucastnik neni v BISu?{' '}
                  <Button
                    secondary
                    small
                    onClick={() => {
                      openAddNewUser()
                    }}
                  >
                    Přidej nového uživatele
                  </Button>
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </StyledModal>
  )
}
