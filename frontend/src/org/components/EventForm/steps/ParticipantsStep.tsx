import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import type { Event, User, UserPayload } from 'app/services/bisTypes'
import { StyledModal } from 'components'
import { UserForm } from 'components/UserForm/UserForm'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { merge } from 'lodash'
import { FC, useState } from 'react'
import styles from './ParticipantsStep.module.scss'
import { Applications } from './registration/Applications'
import { Participants } from './registration/Participants'

export enum ApplicationStates {
  approved = 'approved',
  pending = 'pending',
  rejected = 'rejected',
}

export const ParticipantsStep: FC<{
  event: Event
  onlyApplications?: boolean
}> = ({ event, onlyApplications }) => {
  const [highlightedApplication, setHighlightedApplication] =
    useState<string[]>()
  const [highlightedParticipant, setHighlightedParticipant] = useState<string>()
  const [userModalOpen, setUserModalOpen] = useState(false)
  const [userModalData, setUserModalData] = useState<User | undefined>()
  const [updateUser, updateUserStatus] = api.endpoints.updateUser.useMutation()
  const [createUser, createUserStatus] = api.endpoints.createUser.useMutation()

  const [lastAddedId, setLastAddedId] = useState<string>()
  const [timeOfLastAddition, setTimeOfLastAddition] = useState<number>(0)

  const showMessage = useShowMessage()
  const handleCancelUserForm = () => {
    setUserModalOpen(false)
  }
  const [patchEvent, patchEventStatus] = api.endpoints.updateEvent.useMutation()

  const userModalTitle = userModalData
    ? `Úprava dat účastnice/účastníka ${userModalData.first_name} ${userModalData.last_name}`
    : 'Nový účastník'
  const { data: applicationsData } =
    api.endpoints.readEventApplications.useQuery(
      event
        ? {
            eventId: event.id,
            pageSize: 10000,
          }
        : skipToken,
    )

  const handleClickEditParticipant = (data: User) => {
    setUserModalData(data)
    setUserModalOpen(true)
  }

  useShowApiErrorMessage(createUserStatus.error)
  useShowApiErrorMessage(updateUserStatus.error)

  const { data: participants } = api.endpoints.readEventParticipants.useQuery({
    eventId: event.id,
  })

  const addParticipant = async (newParticipantId: string) => {
    let newParticipants: string[] = []

    if (participants) {
      newParticipants = participants.results.map(p => p.id)
    }
    newParticipants.push(newParticipantId)

    await patchEvent({
      id: event.id,
      event: {
        record: {
          participants: newParticipants,
          contacts: [],
          number_of_participants: null,
          number_of_participants_under_26: null,
        },
      },
    }).unwrap()
  }

  const handleSubmitUserForm = async (data: UserPayload, id?: string) => {
    // if id is passed, update user
    if (id) {
      await updateUser({ id, patchedUser: data }).unwrap()
      // say that it was success
      showMessage({
        type: 'success',
        message: 'Změny byly uloženy',
      })
    }
    // otherwise create new user and add them as participant
    else {
      const fixedData = merge({ donor: null, offers: null }, data)
      // then we create the user and add them as participant
      const { id: userId } = await createUser(fixedData).unwrap()
      await addParticipant(userId)
      // say that it was success
      showMessage({
        type: 'success',
        message: 'Nový účastník byl úspěšně vytvořen a přidán',
      })
    }
    // and if everything works, close the form
    setUserModalOpen(false)
  }
  /** creates a new object, where the keys are the application IDs
   * and the values are the corresponding user IDs for each approved
   * application */
  const approvedApplicationsMap: { [s: string]: string } | undefined =
    applicationsData &&
    applicationsData.results
      .filter(app => app.state === ApplicationStates.approved)
      .reduce<{ [appId: string]: string }>((appsMap, app) => {
        if (app.user) appsMap[app.id.toString()] = app.user
        return appsMap
      }, {})

  /** iterates over the created object from the first part and groups
   * together the application IDs by their corresponding user IDs */
  const participantsMap: { [userId: string]: string[] } | undefined = {}
  if (approvedApplicationsMap)
    for (const [appId, userId] of Object.entries(approvedApplicationsMap)) {
      // If the user ID is not already in the participants map, add it with the current application ID as the first item in the array.
      if (userId) {
        if (!participantsMap[userId]) {
          participantsMap[userId] = [appId]
          // If the user ID is already in the participants map, add the current application ID to the array.
        } else {
          participantsMap[userId].push(appId)
        }
      }
    }

  return (
    <div className={styles.participantsContainer}>
      <StyledModal
        title={userModalTitle}
        open={userModalOpen}
        onClose={handleCancelUserForm}
      >
        <UserForm
          id={(userModalData?.id ?? 'new') + '-participant'}
          initialData={userModalData}
          onCancel={handleCancelUserForm}
          onSubmit={handleSubmitUserForm}
          loading={patchEventStatus.isLoading}
        />
      </StyledModal>
      <Applications
        // @ts-ignore
        event={event}
        highlightedApplications={highlightedApplication}
        chooseHighlightedApplication={id =>
          setHighlightedParticipant(
            approvedApplicationsMap && id && approvedApplicationsMap[id],
          )
        }
        withParticipants={!onlyApplications}
        className={styles.centeredTableBlock}
        openAddNewUser={() => {
          setUserModalOpen(true)
        }}
      />
      {!onlyApplications && (
        <Participants
          eventId={event.id}
          highlightedParticipant={highlightedParticipant}
          chooseHighlightedParticipant={id => {
            if (id && participantsMap)
              setHighlightedApplication(participantsMap[id])
            else {
              setHighlightedApplication(undefined)
            }
          }}
          eventName={event.name}
          participantsMap={participantsMap}
          onClickAddNewParticipant={() => {
            setUserModalData(undefined)
            setUserModalOpen(true)
          }}
          onEditUser={handleClickEditParticipant}
          lastAddedId={lastAddedId}
          timeOfLastAddition={timeOfLastAddition}
          onAddNewParticipant={({ id, time }: { id: string; time: number }) => {
            setLastAddedId(id)
            setTimeOfLastAddition(time)
          }}
          createUser={createUser}
          updateUser={updateUser}
        />
      )}
    </div>
  )
}
