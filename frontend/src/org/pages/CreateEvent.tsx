import { api } from 'app/services/bis'
import {
  Breadcrumbs,
  Error,
  Loading,
  useCreateOrSelectLocation,
} from 'components'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { useCurrentUser } from 'hooks/currentUser'
import { useReadFullEvent } from 'hooks/readFullEvent'
import { useTitle } from 'hooks/title'
import { omit, startsWith } from 'lodash'
import merge from 'lodash/merge'
import { EventForm, EventSubmitShape, QualificationGuide } from 'org/components'
import { useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { toDataURL } from 'utils/helpers'
import { event2payload } from './UpdateEvent'

export const CreateEvent = () => {
  useTitle('Nová akce')
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const cloneEventId = Number(searchParams.get('klonovat'))

  const [isSubmitting, setIsSubmitting] = useState(false)

  const showMessage = useShowMessage()

  const { data: currentUser } = useCurrentUser()

  const {
    data: eventToClone,
    isLoading: isEventToCloneLoading,
    error: eventToCloneError,
  } = useReadFullEvent(cloneEventId)

  const [createEvent, createEventStatus] =
    api.endpoints.createEvent.useMutation()
  const [createEventQuestion, createEventQuestionStatus] =
    api.endpoints.createEventQuestion.useMutation()
  const [createEventImage, createEventImageStatus] =
    api.endpoints.createEventImage.useMutation()

  const createOrSelectLocation = useCreateOrSelectLocation()

  useShowApiErrorMessage(
    createEventStatus.error,
    'Nepodařilo se nám uložit akci',
  )
  useShowApiErrorMessage(
    createEventQuestionStatus.error,
    'Nepodařilo se nám uložit otázku',
  )
  useShowApiErrorMessage(
    createEventImageStatus.error,
    'Nepodařilo se nám uložit obrázek',
  )

  const initialData = useMemo(() => {
    if (!eventToClone)
      return { other_organizers: currentUser ? [currentUser] : [] } // pre-fill current user into organizers
    const eventToCloneFixed = omit(eventToClone, [
      'id',
      'start',
      'start_time',
      'end',
      'record',
      'is_canceled',
      'is_complete',
      'is_closed',
    ])
    return event2payload(eventToCloneFixed)
  }, [currentUser, eventToClone])

  if (eventToCloneError) return <Error error={eventToCloneError} />

  if (cloneEventId > 0 && (isEventToCloneLoading || !eventToClone))
    return <Loading>Stahujeme akci ke zklonování</Loading>

  if (
    isSubmitting ||
    createEventStatus.isLoading ||
    createEventQuestionStatus.isLoading ||
    createEventImageStatus.isLoading
  )
    return <Loading>Ukládáme akci</Loading>

  const handleSubmit = async ({
    main_image,
    images,
    questions,
    ...data
  }: EventSubmitShape) => {
    try {
      setIsSubmitting(true)
      // ***location***
      const locationId = await createOrSelectLocation(data.location)

      // save the new event
      const event = await createEvent(
        merge({}, data, { location: locationId, record: null, finance: null }),
      ).unwrap()

      try {
        // save questions
        if (questions) {
          await Promise.all(
            questions.map((question, order) =>
              createEventQuestion({
                eventId: event.id,
                question: { ...question, order },
              }).unwrap(),
            ),
          )
        }

        // get all images and convert them to base64 and save them
        // because api saves images only in base64 form
        // collect
        const allImagesMixed = [
          ...(main_image ? [main_image.image] : []),
          ...(images.map(image => image.image) ?? []),
        ].filter(image => Boolean(image))
        // convert to base64
        const allImagesBase64 = (
          (
            await Promise.allSettled(
              allImagesMixed.map(image =>
                !image || startsWith(image, 'data:') ? image : toDataURL(image),
              ),
            )
          ).filter(
            result => result.status === 'fulfilled',
          ) as PromiseFulfilledResult<string>[]
        ).map(result => result.value)
        // save
        await Promise.all(
          allImagesBase64.map((image, order) =>
            createEventImage({
              eventId: event.id,
              image: { image, order },
            }).unwrap(),
          ),
        )
      } catch (error) {
        // when saving questions or images fails, we want to handle it differently
        // because the event already exists...
        navigate(`/org/akce/${event.id}/upravit`)
        showMessage({
          message:
            'Akce byla vytvořena, ale něco se nepovedlo. Zkuste to opravit',
          type: 'warning',
        })

        setIsSubmitting(false)
        return
      }

      navigate(`/org/akce/${event.id}`)
      showMessage({ message: 'Akce byla úspěšně vytvořena', type: 'success' })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    navigate('/org')
  }

  return (
    <>
      <Breadcrumbs eventToClone={eventToClone && eventToClone.name} />
      <EventForm
        id={cloneEventId ? `clone-${cloneEventId}` : 'new'}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        initialData={initialData}
        eventToEdit={false}
      />
      <QualificationGuide />
    </>
  )
}
