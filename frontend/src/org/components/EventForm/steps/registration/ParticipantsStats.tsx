import { api } from 'app/services/bis'
import type { Event } from 'app/services/bisTypes'
import { FC } from 'react'
import styles from '../ParticipantsStep.module.scss'
import type * as original from 'app/services/testApi'
import { ApplicationStates } from '../ParticipantsStep'

export const ParticipantsStats: FC<{
  otherOrganizers: original.User[] | undefined
  event: Event
}> = ({ otherOrganizers, event }) => {
  const { data: applicationsData, isLoading: isReadApplicationsLoading } =
    api.endpoints.readEventApplications.useQuery({
      eventId: event.id,
      pageSize: 10000,
    })

  const { data: participantsData, isLoading: isReadParticipantsLoading } =
    api.endpoints.readEventParticipants.useQuery({
      eventId: event.id,
      pageSize: 10000,
    })

  let applications = applicationsData ? applicationsData.results : []
  let participants = participantsData ? participantsData.results : []
  let organizers = otherOrganizers ? otherOrganizers : []

  const applicationsPending = applications.filter(
    app => app.state === ApplicationStates.pending,
  )

  const applicationsAccepted = applications.filter(
    app => app.state === ApplicationStates.approved,
  )

  const applicationsRejected = applications.filter(
    app => app.state === ApplicationStates.rejected,
  )

  let allUsers = [...participants, ...organizers]
  let zeroToSix = 0
  let sevenToFifteen = 0
  let sixteenToEighteen = 0
  let nineteenToTwentySix = 0
  let twentySevenToInfinity = 0
  let unknownAge = 0

  allUsers.forEach(user => {
    const age = user.birthday
      ? ageDifference(new Date(user.birthday), new Date(event.start))
      : undefined
    if (age === undefined) {
      unknownAge++
    } else if (age < 7) {
      zeroToSix++
    } else if (age < 16) {
      sevenToFifteen++
    } else if (age < 19) {
      sixteenToEighteen++
    } else if (age < 27) {
      nineteenToTwentySix++
    } else {
      twentySevenToInfinity++
    }
  })

  return (
    <>
      {!isReadApplicationsLoading && !isReadParticipantsLoading ? (
        <div className={styles.StatsContainer}>
          Počet účastníků: <b>{participants.length + organizers.length}</b>, z
          toho: organizátoři=<b>{organizers.length}</b>, účastníci=
          <b>{participants.length}</b>
          <br />
          Statistika ůčastníků: 0-6 let=<b>{zeroToSix}</b>, 7-15 let:=
          <b>{sevenToFifteen}</b>, 16-18 let=<b>{sixteenToEighteen}</b>, 19-26
          let=<b>{nineteenToTwentySix}</b>, 27+let=
          <b>{twentySevenToInfinity}</b>, celkem do 26 let=
          <b>
            {zeroToSix +
              sevenToFifteen +
              sixteenToEighteen +
              nineteenToTwentySix}
          </b>
          {unknownAge > 0 ? (
            <>
              , neznámý věk=<b>{unknownAge}</b>
            </>
          ) : (
            ''
          )}
          <br />
          Počet přihlášených: <b>{applications.length}</b>, z toho: přijatí=
          <b>{applicationsAccepted.length}</b>, zamítnutí=
          <b>{applicationsRejected.length}</b>, čekající=
          <b>{applicationsPending.length}</b>
          <br />
        </div>
      ) : (
        ''
      )}
    </>
  )
}

const ageDifference = (birthday: Date, comparingDate: Date): number => {
  var ageyear = comparingDate.getFullYear() - birthday.getFullYear()
  var agemonth = comparingDate.getMonth() - birthday.getMonth()
  var ageday = comparingDate.getDate() - birthday.getDate()

  if (agemonth < 0) {
    ageyear--
  } else if (agemonth == 0 && ageday < 0) {
    ageyear--
  }

  return ageyear
}
