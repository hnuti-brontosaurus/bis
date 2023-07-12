import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import type { User, UserPayload } from 'app/services/bisTypes'
import classNames from 'classnames'
import {
  Actions,
  Button,
  EmptyListPlaceholder,
  Loading,
  SelectUnknownUser,
  StyledModal,
  TableCellIconButton,
} from 'components'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { ImportParticipants } from 'org/components/ImportParticipants/ImportParticipants'
import { ConfirmedUser } from 'org/components/ImportParticipants/ImportParticipantsList/ImportParticipantsList'
import { FC, useState } from 'react'
import { FaTrash as Bin, FaUserEdit as EditUser } from 'react-icons/fa'
import colors from 'styles/colors.module.scss'
import { formatAddress, formatDateTime } from 'utils/helpers'
import { ApplicationStates } from '../ParticipantsStep'
import styles from '../ParticipantsStep.module.scss'
import { ShowApplicationModal } from './ShowApplicationModal'
import { useExportParticipantsList } from './useExportParticipantsList'

export const Participants: FC<{
  eventId: number
  eventName: string
  chooseHighlightedParticipant: (id: string | undefined) => void
  highlightedParticipant?: string
  participantsMap?: { [s: string]: string[] }
  onClickAddNewParticipant: () => void
  onEditUser: (user: User) => void
  lastAddedId: string | undefined
  timeOfLastAddition: number
  onAddNewParticipant: ({ id, time }: { id: string; time: number }) => void
  createUser: ReturnType<typeof api.endpoints.createUser.useMutation>[0]
  updateUser: ReturnType<typeof api.endpoints.updateUser.useMutation>[0]
}> = ({
  eventId,
  eventName,
  highlightedParticipant,
  chooseHighlightedParticipant,
  participantsMap,
  onClickAddNewParticipant,
  onEditUser,
  lastAddedId,
  timeOfLastAddition,
  onAddNewParticipant,
  createUser,
  updateUser,
}) => {
  const { data: participants, isLoading: isReadParticipantsLoading } =
    api.endpoints.readEventParticipants.useQuery({ eventId, pageSize: 10000 })

  const [showShowApplicationModal, setShowShowApplicationModal] =
    useState<boolean>(false)

  const showMessage = useShowMessage()

  const [currentParticipantId, setCurrentParticipantId] = useState<string>()
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const { data: membershipCategories } =
    api.endpoints.readMembershipCategories.useQuery({})

  const { data: administrationUnits } =
    api.endpoints.readAdministrationUnits.useQuery({ pageSize: 2000 })

  const { data: currentParticipant } = api.endpoints.readUser.useQuery(
    currentParticipantId ? { id: currentParticipantId } : skipToken,
  )

  const [patchEvent, patchEventStatus] = api.endpoints.updateEvent.useMutation()
  const [highLightedRow, setHighlightedRow] = useState<string>()

  useShowApiErrorMessage(patchEventStatus.error)

  const [exportParticipantsList, { isLoading: isExportLoading }] =
    useExportParticipantsList()

  const addParticipant = async (newParticipantId: string) => {
    let newParticipants: string[] = []

    if (participants) {
      newParticipants = participants.results.map(p => p.id)
    }
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
    }).unwrap()

    onAddNewParticipant({ id: newParticipantId, time: Date.now() })
  }

  const [updateApplication] = api.endpoints.updateEventApplication.useMutation()

  const addParticipants = async (newParticipantIds: string[]) => {
    const allParticipants: string[] = []

    if (participants) {
      allParticipants.push(...participants.results.map(p => p.id))
    }
    allParticipants.push(...newParticipantIds)

    await patchEvent({
      id: eventId,
      event: {
        record: {
          participants: allParticipants,
          contacts: [],
          number_of_participants: null,
          number_of_participants_under_26: null,
        },
      },
    }).unwrap()

    newParticipantIds.forEach(id => {
      onAddNewParticipant({ id, time: Date.now() })
    })
  }

  const handleClickNewParticipant = () => {
    onClickAddNewParticipant()
  }

  /**
   * Handle removing a participant
   */
  const [removeModalOpen, setRemoveModalOpen] = useState(false)
  const [removeModalData, setRemoveModalData] = useState<User | undefined>()
  const handleClickRemoveParticipant = (data: User) => {
    setRemoveModalData(data)
    setRemoveModalOpen(true)
  }

  const handleCancelRemoveParticipant = () => {
    setRemoveModalOpen(false)
  }

  const handleConfirmRemoveParticipant = async () => {
    try {
      // make array of participants without this one
      const updatedParticipants = participants?.results
        .map(p => p.id)
        .filter(id => id !== removeModalData!.id)
      await patchEvent({
        id: eventId,
        event: {
          record: {
            participants: updatedParticipants,
            contacts: [],
          },
        },
      }).unwrap()

      // make applications assigned to this user 'pending'
      if (
        participantsMap &&
        removeModalData &&
        participantsMap[removeModalData.id]
      ) {
        for (let i of participantsMap[removeModalData.id]) {
          await updateApplication({
            id: Number(i),
            eventId: eventId,
            patchedEventApplication: {
              state: ApplicationStates.pending,
              user: null,
            },
          })
        }
      }

      showMessage({
        type: 'success',
        message: `Uživatel/ka ${removeModalData!.first_name} ${
          removeModalData!.last_name
        } byl/a úspěšně smazán/a ze seznamu účastníků`,
      })
    } finally {
      setRemoveModalOpen(false)
    }
  }

  /**
   * Save imported participants
   */
  const handleSaveImportedParticipants = async (data: ConfirmedUser[]) => {
    const existingParticipants = data.filter(
      datum => 'id' in datum && datum.id,
    ) as ({ id: string } & Partial<UserPayload>)[]
    const newParticipantsData = data.filter(
      datum => !('id' in datum && datum.id),
    ) as UserPayload[]

    // create non-existent people
    const newParticipantsOutcome = await Promise.allSettled(
      newParticipantsData.map(datum => createUser(datum).unwrap()),
    )

    const newParticipants = newParticipantsOutcome
      .map(outcome =>
        outcome.status === 'fulfilled' ? outcome.value : undefined,
      )
      .filter(user => Boolean(user)) as User[]

    // save participants
    await addParticipants(
      existingParticipants
        .map(p => p.id)
        .concat(newParticipants.map(p => p.id)),
    )

    // update existent people
    const updatedUserOutcome = await Promise.allSettled(
      existingParticipants.map(async ({ id, ...data }) => {
        await updateUser({ id, patchedUser: data })
      }),
    )

    const failedCreate = newParticipantsOutcome
      .map((o, i) => [o, i] as const)
      .filter(([o]) => o.status === 'rejected')
      .map(([, i]) => newParticipantsData[i])

    const failedUpdate = updatedUserOutcome
      .map((o, i) => [o, i] as const)
      .filter(([o]) => o.status === 'rejected')
      .map(([, i]) => existingParticipants[i])

    const failedImports = { create: failedCreate, update: failedUpdate }

    return failedImports
  }

  const removeModalTitle = removeModalData
    ? `Opravdu chcete smazat účastnici/účastníka ${removeModalData.first_name} ${removeModalData.last_name} z akce ${eventName}?`
    : undefined

  return (
    <div className={styles.ListContainer}>
      <StyledModal
        title={removeModalTitle}
        open={removeModalOpen}
        onClose={handleCancelRemoveParticipant}
      >
        <RemoveParticipantConfirmDialog
          onConfirm={handleConfirmRemoveParticipant}
          onCancel={handleCancelRemoveParticipant}
        />
      </StyledModal>

      <h2>Účastníci</h2>
      <div className={styles.buttonsContainer}>
        <Button
          secondary
          small
          type="button"
          onClick={() => {
            exportParticipantsList({ eventId })
          }}
          isLoading={isExportLoading}
        >
          Export do excelu
        </Button>
        {/* TODO It would be awesome if import and export use excel in the same format */}
        <div className={styles.excelButtons}>
          <ImportParticipants onConfirm={handleSaveImportedParticipants} />
        </div>
        <Button type="button" primary small onClick={handleClickNewParticipant}>
          Přidej nového účastníka
        </Button>
      </div>
      {!isReadParticipantsLoading ? (
        <div className={styles.existingParticipantContainer}>
          <div>Přidat účastníka z BISu:</div>
          <SelectUnknownUser
            value={selectedUser ?? undefined}
            onChange={async selectedUser => {
              setSelectedUser(selectedUser)
              if (selectedUser) {
                await addParticipant(selectedUser.id)
                setSelectedUser(null)
              }
            }}
            onBirthdayError={message => {
              showMessage({
                type: 'error',
                message: 'Nepodařilo se přidat uživatele',
                detail: message,
              })
            }}
          />
          {participants && participants.results && (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Jméno</th>
                  <th>příjmení</th>
                  <th>datum narození</th>
                  <th>adresa</th>
                  <th>telefon</th>
                  <th>e-mail</th>
                  <th>
                    <EditUser className={classNames(styles.iconHead)} />
                  </th>
                  <th>
                    <Bin className={classNames(styles.iconHead)}></Bin>
                  </th>
                </tr>
              </thead>
              <tbody>
                {participants.results.map((participant: User) => (
                  <tr
                    key={participant.id}
                    className={classNames(
                      highlightedParticipant === participant.id
                        ? styles.highlightedRow
                        : '',
                      lastAddedId === participant.id &&
                        timeOfLastAddition > Date.now() - 30000 &&
                        styles.lightUp,
                      highLightedRow === participant.id
                        ? styles.highlightedRow
                        : '',
                    )}
                    onMouseEnter={() => {
                      setHighlightedRow(participant.id)
                      chooseHighlightedParticipant(participant.id)
                    }}
                    onMouseLeave={() => {
                      setHighlightedRow(undefined)
                      chooseHighlightedParticipant(undefined)
                    }}
                    onClick={() => {
                      setShowShowApplicationModal(true)
                      setCurrentParticipantId(participant.id)
                    }}
                  >
                    <td>
                      {`${participant.first_name}${
                        participant.nickname && `(${participant.nickname})`
                      }`}
                    </td>
                    <td>{participant.last_name}</td>
                    <td>{formatDateTime(participant.birthday)}</td>
                    <td>
                      {participant.address &&
                        formatAddress(participant.address)}
                    </td>
                    <td>{participant.phone}</td>
                    <td>{participant.email}</td>
                    <TableCellIconButton
                      icon={EditUser}
                      action={() => onEditUser(participant)}
                      tooltipContent="Upravit účastníka"
                      color={colors.yellow}
                      ariaLabel={`Upravit účastníka ${participant.first_name} ${participant.last_name}`}
                    />
                    <TableCellIconButton
                      icon={Bin}
                      action={() => handleClickRemoveParticipant(participant)}
                      tooltipContent="Smazat účastníka"
                      color={colors.error}
                      ariaLabel={`Smazat účastníka ${participant.first_name} ${participant.last_name}`}
                    />
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {participants?.results?.length === 0 && (
            <EmptyListPlaceholder label="Zatím nebyli přidáni žádní účastníci." />
          )}
        </div>
      ) : (
        <Loading>Stahujeme účastníky</Loading>
      )}
      {currentParticipant && (
        <ShowApplicationModal
          open={showShowApplicationModal}
          onClose={() => {
            setShowShowApplicationModal(false)
            setHighlightedRow(undefined)
          }}
          userId={currentParticipantId}
          currentParticipant={currentParticipant}
          eventName={eventName}
          eventId={eventId}
          categories={membershipCategories?.results ?? []}
          administrationUnits={
            administrationUnits ? administrationUnits.results : []
          }
          participantsMap={participantsMap}
        ></ShowApplicationModal>
      )}
    </div>
  )
}

const RemoveParticipantConfirmDialog = ({
  onConfirm,
  onCancel,
}: {
  onConfirm: () => void
  onCancel: () => void
}) => {
  const [saving, setSaving] = useState(false)
  const handleClickConfirm = async () => {
    setSaving(true)
    try {
      await onConfirm()
    } finally {
      setSaving(false)
    }
  }

  if (saving) return <Loading>Mažeme účastníka</Loading>

  return (
    <Actions>
      <Button secondary onClick={onCancel}>
        Ne
      </Button>
      <Button danger onClick={handleClickConfirm}>
        Ano, smazat
      </Button>
    </Actions>
  )
}
