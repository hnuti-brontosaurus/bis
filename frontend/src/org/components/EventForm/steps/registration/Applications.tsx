import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import type { AdministrationUnit, Event } from 'app/services/bisTypes'
import { EventApplication } from 'app/services/bisTypes'
import classNames from 'classnames'
import {
  Button,
  EmptyListPlaceholder,
  Loading,
  TableCellIconButton,
} from 'components'
import { useRejectApplication } from 'hooks/rejectApplication'
import { FC, useState } from 'react'
import {
  FaTrash as Bin,
  FaTrashRestoreAlt,
  FaUserPlus as AddUser,
} from 'react-icons/fa'
import colors from 'styles/colors.module.scss'
import { formatDateTime } from 'utils/helpers'
import { ApplicationStates } from '../ParticipantsStep'
import styles from '../ParticipantsStep.module.scss'
import { AddParticipantModal } from './AddParticipantModal'
import { NewApplicationModal } from './NewApplicationModal'
import { ShowApplicationModal } from './ShowApplicationModal'
import { useExportAttendanceList } from './useExportAttendanceList'

export const Applications: FC<{
  event: Event
  chooseHighlightedApplication: (id: string | undefined) => void
  highlightedApplications?: string[]
  withParticipants?: boolean
  className: string
  openAddNewUser: () => void
}> = ({
  event,
  highlightedApplications,
  chooseHighlightedApplication,
  withParticipants,
  className,
  openAddNewUser,
}) => {
  const [showNewApplicationModal, setShowNewApplicationModal] =
    useState<boolean>(false)
  const [showAddParticipantModal, setShowAddParticipantModal] =
    useState<boolean>(false)
  const [showShowApplicationModal, setShowShowApplicationModal] =
    useState<boolean>(false)
  const [highLightedRow, setHighlightedRow] = useState<number>()
  const [currentApplicationId, setCurrentApplicationId] = useState<number>()

  const [rejectApplication] = useRejectApplication()

  const [updateApplication] = api.endpoints.updateEventApplication.useMutation()

  const restoreApplication = async (
    application: EventApplication,
    event: { id: number; name: string },
  ) => {
    await updateApplication({
      id: application.id,
      eventId: event.id,
      patchedEventApplication: {
        state: ApplicationStates.pending,
      },
    })
  }

  const { data: membershipCategories } =
    api.endpoints.readMembershipCategories.useQuery({})
  const { data: administrationUnitsData } =
    api.endpoints.readAdministrationUnits.useQuery({ pageSize: 2000 })

  const { data: participants } = api.endpoints.readEventParticipants.useQuery({
    eventId: event.id,
    pageSize: 10000,
  })

  const { data: currentApplication } =
    api.endpoints.readEventApplication.useQuery(
      event.id && currentApplicationId
        ? {
            eventId: event.id,
            applicationId: currentApplicationId,
          }
        : skipToken,
    )

  const { data: applicationsData, isLoading: isReadApplicationsLoading } =
    api.endpoints.readEventApplications.useQuery({
      eventId: event.id,
      pageSize: 10000,
    })

  let applications = applicationsData ? applicationsData.results : []

  const applicationsPending = applications.filter(
    app => app.state === ApplicationStates.pending,
  )

  const applicationsAccepted = applications.filter(
    app => app.state === ApplicationStates.approved,
  )

  const applicationsRejected = applications.filter(
    app => app.state === ApplicationStates.rejected,
  )

  const handleShowApplication = (id: number) => {
    setCurrentApplicationId(id)
    setShowShowApplicationModal(true)
  }

  const administrationUnits =
    administrationUnitsData && administrationUnitsData.results
      ? administrationUnitsData.results
      : []

  const getEventAdministrationUnits = (event: Event) => {
    const names: string[] = []
    for (const id of event.administration_units) {
      const administrationUnit = administrationUnits.find(
        (d: AdministrationUnit) => d.id === id,
      )
      if (administrationUnit) {
        names.push(administrationUnit.name)
      }
    }
    return names
  }

  const removeApplicationsDuplicates = (arr: EventApplication[]) => {
    const uniqueSet = new Set()
    return arr.filter((obj: EventApplication) => {
      const { first_name, last_name, email, phone } = obj
      const uniqueKey = `${first_name}-${last_name}-${email}-${phone}`
      if (!uniqueSet.has(uniqueKey)) {
        uniqueSet.add(uniqueKey)
        return true
      }
      return false
    })
  }

  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false)

  const generateAndSavePdf = async () => {
    setIsGeneratingPdf(true)
    const { generatePdf } = await import('./participantsPdf')
    const doc = generatePdf(
      removeApplicationsDuplicates(
        applicationsPending.concat(applicationsAccepted),
      ) || [],
      {
        ...event,
        administration_units_names: getEventAdministrationUnits(event),
      },
    )
    await doc.save(`Lidé přihlášení na akci: ${event.name}`, {
      returnPromise: true,
    })
    setIsGeneratingPdf(false)
  }

  const [exportAttendanceList, { isLoading: isExportLoading }] =
    useExportAttendanceList()

  const thereAreApplications = applications && applications.length !== 0

  const ApplicationRow = ({
    application,
    className,
  }: {
    application: EventApplication
    className?: string
  }) => (
    <tr
      key={application.id}
      className={classNames(
        highlightedApplications?.includes(application.id.toString()) &&
          styles.highlightedRow,
        application.state === ApplicationStates.rejected &&
          styles.applicationWithParticipant,
        className,
        highLightedRow === application.id ? styles.highlightedRow : '',
        application.state === ApplicationStates.approved && styles.approvedRow,
      )}
      onMouseEnter={() => {
        setHighlightedRow(application.id)
        chooseHighlightedApplication(application.id.toString())
      }}
      onMouseLeave={() => {
        setHighlightedRow(undefined)
        chooseHighlightedApplication(undefined)
      }}
    >
      <td onClick={() => handleShowApplication(application.id)}>
        {formatDateTime(application.created_at)}
      </td>
      <td onClick={() => handleShowApplication(application.id)}>
        {application.first_name}
      </td>
      <td onClick={() => handleShowApplication(application.id)}>
        {application.last_name}
      </td>
      <td onClick={() => handleShowApplication(application.id)}>
        {application.birthday && formatDateTime(application.birthday)}
      </td>
      <td onClick={() => handleShowApplication(application.id)}>
        {application.phone}
      </td>
      <td onClick={() => handleShowApplication(application.id)}>
        {application.email}
      </td>
      {withParticipants && (
        <TableCellIconButton
          icon={AddUser}
          action={() => {
            setCurrentApplicationId(application.id)
            setShowAddParticipantModal(true)
          }}
          disabled={application.state === ApplicationStates.rejected}
          tooltipContent={'Přidej účastníka'}
          color={colors.bronto}
        />
      )}

      <TableCellIconButton
        icon={
          application.state === ApplicationStates.rejected
            ? FaTrashRestoreAlt
            : Bin
        }
        action={async () => {
          if (application.state === ApplicationStates.rejected) {
            restoreApplication(application, { id: event.id, name: event.name })
          } else {
            rejectApplication({
              application,
              event: { id: event.id, name: event.name },
            })
          }
        }}
        disabled={application.state === 'approved'}
        tooltipContent={
          application.state === 'rejected'
            ? 'Obnov přihlášku'
            : 'Odmítni přihlášku'
        }
        color={
          application.state === ApplicationStates.rejected
            ? colors.bronto
            : colors['error']
        }
      />
    </tr>
  )

  return (
    <>
      <div className={classNames(styles.ListContainer, className)}>
        <h2>Přihlášení</h2>
        <div className={styles.buttonsContainer}>
          <Button
            secondary
            small
            type="button"
            onClick={() => {
              exportAttendanceList({ eventId: event.id, format: 'xlsx' })
            }}
            isLoading={isExportLoading}
          >
            Export do excelu
          </Button>
          <Button
            secondary
            small
            type="button"
            isLoading={isGeneratingPdf}
            onClick={() => generateAndSavePdf()}
          >
            Tiskni prezenční listinu
          </Button>
          <Button
            primary
            small
            type="button"
            onClick={() => {
              setShowNewApplicationModal(true)
            }}
          >
            Přidej novou přihlášku
          </Button>
        </div>

        {!isReadApplicationsLoading ? (
          <div>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>datum podání</th>
                  <th>jméno</th>
                  <th>příjmení</th>
                  <th>datum narození</th>
                  <th>telefon</th>
                  <th>e-mail</th>
                  {withParticipants && (
                    <th>
                      <AddUser className={classNames(styles.iconHead)} />
                    </th>
                  )}
                  <th>
                    <Bin className={classNames(styles.iconHead)}></Bin>
                  </th>
                </tr>
              </thead>
              <tbody>
                <>
                  {applicationsPending.map((application: EventApplication) => (
                    <ApplicationRow
                      key={application.id}
                      application={application}
                    />
                  ))}
                  {applicationsAccepted.length > 0 && (
                    <tr>
                      <td colSpan={5} className={styles.oneCellRow}>
                        Přidání do účastníků
                      </td>
                    </tr>
                  )}
                  {applicationsAccepted.map((application: EventApplication) => (
                    <ApplicationRow
                      key={application.id}
                      application={application}
                    />
                  ))}
                  {applicationsRejected.length > 0 && (
                    <tr>
                      <td colSpan={5} className={styles.oneCellRow}>
                        Odmítnuté přihlášky
                      </td>
                    </tr>
                  )}

                  {applicationsRejected.map((application: EventApplication) => (
                    <ApplicationRow
                      key={application.id}
                      application={application}
                    />
                  ))}
                </>
              </tbody>
            </table>

            {!thereAreApplications && (
              <EmptyListPlaceholder label="Ještě se nikdo nepřihlásil" />
            )}
          </div>
        ) : (
          <Loading>Stahujeme přihlášky</Loading>
        )}
        <NewApplicationModal
          open={showNewApplicationModal}
          onClose={() => {
            setShowNewApplicationModal(false)
          }}
          event={event}
        ></NewApplicationModal>

        {currentApplication && (
          <AddParticipantModal
            open={showAddParticipantModal}
            onClose={() => {
              setShowAddParticipantModal(false)
            }}
            currentApplication={currentApplication}
            defaultUserData={currentApplication}
            eventId={event.id}
            eventParticipants={
              participants ? participants?.results.map(({ id }) => id) : []
            }
            openAddNewUser={openAddNewUser}
          />
        )}
        {currentApplication && (
          <ShowApplicationModal
            open={showShowApplicationModal}
            onClose={() => {
              setCurrentApplicationId(undefined)
              setHighlightedRow(undefined)
              setShowShowApplicationModal(false)
            }}
            currentApplication={currentApplication}
            eventName={event.name}
            eventId={event.id}
            categories={membershipCategories?.results ?? []}
            administrationUnits={administrationUnits}
          ></ShowApplicationModal>
        )}
      </div>
    </>
  )
}
