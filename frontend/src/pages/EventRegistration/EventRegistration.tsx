import { api } from 'app/services/bis'
import type { EventApplicationPayload } from 'app/services/bisTypes'
import { Error, ExternalButtonLink, Loading, PageHeader } from 'components'
import { useShowApiErrorMessage } from 'features/systemMessage/useSystemMessage'
import { useCurrentUser } from 'hooks/currentUser'
import {
  useClearPersistentForm,
  useDirectPersistForm,
  usePersistentFormData,
} from 'hooks/persistForm'
import { useTitle } from 'hooks/title'
import { getRegistrationMethod } from 'org/components/EventForm/EventForm'
import { useState } from 'react'
import { FaRegCalendarAlt } from 'react-icons/fa'
import { GrLocation } from 'react-icons/gr'
import { useParams, useSearchParams } from 'react-router-dom'
import { formatDateRange } from 'utils/helpers'
import styles from './EventRegistration.module.scss'
import {
  EventRegistrationForm,
  FinishedStep,
  RegistrationFormShapeWithStep,
} from './EventRegistrationForm'

export const EventRegistration = () => {
  const [searchParams] = useSearchParams()
  const next = searchParams.get('next') ?? 'https://brontosaurus.cz'

  const params = useParams()
  const eventId = Number(params.eventId)
  const { data: user, isAuthenticated } = useCurrentUser()

  // fetch event
  const {
    data: event,
    isError: isEventError,
    error: eventError,
  } = api.endpoints.readWebEvent.useQuery({ id: eventId })

  useTitle(`Přihláška na akci ${event?.name ?? ''}`)

  const [createEventApplication, { error: savingError }] =
    api.endpoints.createEventApplication.useMutation()

  const formData = usePersistentFormData(
    'registration',
    String(eventId),
  ) as RegistrationFormShapeWithStep
  const persist = useDirectPersistForm('registration', String(eventId))
  const clearPersistentData = useClearPersistentForm(
    'registration',
    String(eventId),
  )

  useShowApiErrorMessage(
    savingError,
    'Nepodařilo se nám uložit přihlášku. Zkuste to znovu.',
  )

  const [isSaving, setIsSaving] = useState(false)

  if (isEventError) return <Error error={eventError}></Error>

  if (isSaving) return <Loading>Ukládáme přihlášku</Loading>

  if (isAuthenticated && !user) return <Loading>Ověřujeme uživatele</Loading>

  if (!event) return <Loading>Připravujeme přihlášku</Loading>

  // akce už proběhla?
  // we make sure that it's still possible to register to events ending today
  // by setting both dates to midnight
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const end = new Date(event.end)
  end.setHours(0, 0, 0, 0)
  if (today > end)
    return (
      <Error message={`Akce ${event.name} už proběhla`}>
        <ExternalButtonLink
          tertiary
          href="https://brontosaurus.cz/dobrovolnicke-akce/"
        >
          Zkuste jinou z našich akcí
        </ExternalButtonLink>
      </Error>
    )

  if (!event.registration)
    return <Error message="Není zadefinována registrace."></Error>

  const registrationMethod = getRegistrationMethod(event)

  if (registrationMethod === 'full')
    return (
      <Error message="Tato akce je plná">
        <a href="https://brontosaurus.cz/dobrovolnicke-akce/">
          Zkuste jinou z našich akcí
        </a>
      </Error>
    )

  if (registrationMethod === 'none')
    return (
      <Error message="Na tuto akci se nemusíte přihlašovat. Stačí přijít."></Error>
    )

  // when alternative registration link is set, redirect there
  // at this point, we know for sure that alternative_registration_link
  // is available, because we checked it in getRegistrationMethod
  if (registrationMethod === 'other') {
    globalThis.location.replace(
      event.registration.alternative_registration_link as string,
    )
    return <Loading>Přesměrujeme na přihlášku</Loading>
  }

  const handleRestart = () => {
    clearPersistentData()
  }

  const handleFinish = () => {
    clearPersistentData()
    // when finished, go to main brontosaurus site
    globalThis.location.href = next
  }

  const handleSubmit = async (data: EventApplicationPayload) => {
    try {
      setIsSaving(true)
      await createEventApplication({
        application: data,
        eventId,
      }).unwrap()
      clearPersistentData()
      persist({ step: 'finished' })
    } catch (error) {
      persist({ step: 'progress' })
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    // redirect to event detail on brontosaurus.cz
    // TODO set a more generic address (not always dobrovolnicke-akce)
    globalThis.location.href = `https://brontosaurus.cz/dobrovolnicke-akce/detail/${eventId}/`
  }

  return (
    <div>
      <PageHeader>Přihláška na akci {event?.name}</PageHeader>
      <div className={styles.infoBox}>
        <div>
          <FaRegCalendarAlt /> {formatDateRange(event.start, event.end)}
        </div>
        <div>
          <GrLocation /> {event.location?.name}
        </div>
      </div>
      {formData?.step === 'finished' ? (
        <FinishedStep
          message={
            event.registration.questionnaire?.after_submit_text ||
            'Děkujeme za přihlášku!'
          }
          onRestart={handleRestart}
          onFinish={handleFinish}
        />
      ) : (
        <EventRegistrationForm
          id={String(eventId)}
          user={user}
          questionnaire={event.registration.questionnaire ?? undefined}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      )}
    </div>
  )
}
