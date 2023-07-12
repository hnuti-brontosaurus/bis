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
import { FullEvent } from 'hooks/readFullEvent'
import { useTitle } from 'hooks/title'
import { cloneDeep, isEqual, mergeWith } from 'lodash'
import merge from 'lodash/merge'
import { EventForm, InitialEventData } from 'org/components'
import { ApplicationStates } from 'org/components/EventForm/steps/ParticipantsStep'
import { useState } from 'react'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'
import { Optional } from 'utility-types'
import { isEventClosed, sortOrder, withOverwriteArray } from 'utils/helpers'

export const UpdateEvent = () => {
  const params = useParams()
  const eventId = Number(params.eventId)
  const navigate = useNavigate()
  const showMessage = useShowMessage()

  const { event } = useOutletContext<{ event: FullEvent }>()

  // TODO maybe: add star when data are unsaved (also persistent data)
  useTitle(event ? `Upravit akci ${event.name}` : 'Upravit akci')

  const [updateEvent, { error: updateEventError }] =
    api.endpoints.updateEvent.useMutation()
  const [createEventImage, createEventImageStatus] =
    api.endpoints.createEventImage.useMutation()
  const [updateEventImage, updateEventImageStatus] =
    api.endpoints.updateEventImage.useMutation()
  const [removeEventImage, deleteEventImageStatus] =
    api.endpoints.deleteEventImage.useMutation()
  const [createEventQuestion, createEventQuestionStatus] =
    api.endpoints.createEventQuestion.useMutation()
  const [updateEventQuestion, updateEventQuestionStatus] =
    api.endpoints.updateEventQuestion.useMutation()
  const [removeEventQuestion, deleteEventQuestionStatus] =
    api.endpoints.deleteEventQuestion.useMutation()

  useShowApiErrorMessage(updateEventError, 'Nepodařilo se uložit změny')

  useShowApiErrorMessage(
    createEventImageStatus.error,
    'Nepodařilo se uložit fotku',
  )
  useShowApiErrorMessage(
    updateEventImageStatus.error,
    'Nepodařilo se uložit fotku',
  )
  useShowApiErrorMessage(
    deleteEventImageStatus.error,
    'Nepodařilo se smazat fotku',
  )
  useShowApiErrorMessage(
    createEventQuestionStatus.error,
    'Nepodařilo se uložit otázku',
  )
  useShowApiErrorMessage(
    updateEventQuestionStatus.error,
    'Nepodařilo se uložit otázku',
  )
  useShowApiErrorMessage(
    deleteEventQuestionStatus.error,
    'Nepodařilo se smazat otázku',
  )

  const createOrSelectLocation = useCreateOrSelectLocation()

  const [isSubmitting, setIsSubmitting] = useState(false)

  if (isEventClosed(event))
    return (
      <>
        <Breadcrumbs eventName={event && event.name} />
        <Error status={403} message="Tuto akci už nelze upravovat">
          Upravovat akce můžete jen do konce ledna roku následujícího po roce
          konání akce
        </Error>
      </>
    )

  if (isSubmitting) return <Loading>Ukládáme změny</Loading>

  const { images, questions } = event
  const initialEvent = event

  const handleSubmit: Parameters<typeof EventForm>[0]['onSubmit'] = async ({
    main_image: updatedMainImage,
    images: updatedImages,
    questions: updatedQuestions,
    ...event
  }) => {
    try {
      setIsSubmitting(true)
      // ***location***
      const locationId = await createOrSelectLocation(event.location)

      // clean up unfilled fields which cause api problems
      if (event.record?.comment_on_work_done === null)
        delete event.record.comment_on_work_done
      if (event.record?.total_hours_worked === null)
        delete event.record.total_hours_worked

      // make sure we save initial registration data when is_event_full
      if (event.registration?.is_event_full) {
        event.registration = merge({}, initialEvent.registration, {
          is_event_full: true,
        })
      }

      // update event
      await updateEvent({
        id: eventId,
        event: merge({}, event, {
          location: locationId,
        }),
      }).unwrap()

      // ***images***
      // get order from position

      const imagesWithOrder = [
        ...(updatedMainImage ? [updatedMainImage] : []),
        ...updatedImages,
      ]
        .filter(({ image }) => image) // ignore undefined images
        .map((image, order) => ({ ...image, order }))

      const newImages: { image: string; order: number }[] = []
      const imagesToPatch: { id: number; image?: string; order?: number }[] = []
      imagesWithOrder.forEach(image => {
        // save every new image
        // images without id are new
        if (!image.id) return newImages.push(image)
        // images with id, but with different
        else {
          // find original image
          const originalImage = images.find(img => img.id === image.id)

          // if they're same, ignore
          if (
            originalImage!.image.original === image.image &&
            originalImage!.order === image.order
          )
            return
          // otherwise add patch to imagesToPatch
          else {
            const imageToPatch: { id: number; image?: string; order?: number } =
              {
                id: image.id,
              }
            // update order of any image that changed order
            if (originalImage!.order !== image.order)
              imageToPatch.order = image.order
            // update any image that changed
            if (originalImage!.image.original !== image.image)
              imageToPatch.image = image.image

            return imagesToPatch.push(imageToPatch)
          }
        }
      })

      // delete any image that is missing, or any image that has image: null
      const imagesToDelete: { id: number }[] = images.filter(
        img =>
          (img.id && !img.image) ||
          !imagesWithOrder.find(image => image.id === img.id),
      )

      const newImagePromises = newImages.map(image =>
        createEventImage({ eventId, image }).unwrap(),
      )
      const patchedImagePromises = imagesToPatch.map(({ id, ...image }) =>
        updateEventImage({ eventId, id, image }).unwrap(),
      )

      const deletedImagePromises = imagesToDelete.map(({ id }) =>
        removeEventImage({ eventId, id }).unwrap(),
      )

      const imageOutput = await Promise.allSettled([
        ...newImagePromises,
        ...patchedImagePromises,
        ...deletedImagePromises,
      ])
      if (
        imageOutput.some(({ status }) => status === ApplicationStates.rejected)
      )
        showMessage({
          type: 'warning',
          message: 'Některé fotky se nepodařilo uložit',
        })

      // ***questions***
      // save every new question
      // get order from position
      const questionsWithOrder = updatedQuestions.map((question, order) => ({
        ...question,
        order,
      }))
      /// create the questions that are new
      const newQuestionPromises = questionsWithOrder
        .filter(q => !q.id)
        .map(question => createEventQuestion({ eventId, question }).unwrap())
      // update any changed questions
      const patchedQuestionPromises = questionsWithOrder
        .filter(question => {
          const oldQuestion = questions.find(oq => oq.id === question.id)
          // if something is different, patch
          return oldQuestion && !isEqual(oldQuestion, question)
        })
        .map(({ id, ...question }) =>
          updateEventQuestion({ eventId, id: id as number, question }).unwrap(),
        )

      // delete any question that is missing
      const deletedQuestionPromises = questions
        .filter(q => !questionsWithOrder.find(question => question.id === q.id))
        .map(({ id }) => removeEventQuestion({ eventId, id }).unwrap())

      const questionOutput = await Promise.allSettled([
        ...newQuestionPromises,
        ...patchedQuestionPromises,
        ...deletedQuestionPromises,
      ])
      //TODO inform users when something fails
      if (
        questionOutput.some(
          ({ status }) => status === ApplicationStates.rejected,
        )
      )
        showMessage({
          type: 'warning',
          message: 'Některé otázky se nepodařilo uložit',
        })

      navigate(`/org/akce/${eventId}`)
      showMessage({ message: 'Akce byla úspěšně změněna', type: 'success' })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    navigate(`/org/akce/${eventId}`)
  }

  return (
    <>
      <Breadcrumbs eventName={event && event.name} />
      <EventForm
        id={String(eventId)}
        initialData={event2payload(event)}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        eventToEdit={true}
      />
    </>
  )
}

export const event2payload = (
  event: Optional<
    FullEvent,
    'id' | 'start' | 'start_time' | 'end' | 'record' | 'is_canceled'
  >,
): Partial<InitialEventData> => {
  const [main_image, ...otherImages] = event.images
    .map(img => ({
      ...img,
      image: img.image.original,
    }))
    .sort(sortOrder)

  return mergeWith(
    cloneDeep(event),
    {
      group: event?.group?.id,
      category: event?.category?.id,
      program: event?.program?.id,
      intended_for: event?.intended_for?.id,
      propagation: event.propagation && {
        diets: event.propagation.diets.map(diet => diet.id),
      },
      main_image,
      images: otherImages,
      questions: [...event.questions].sort(sortOrder),
    },
    withOverwriteArray,
  )
}
