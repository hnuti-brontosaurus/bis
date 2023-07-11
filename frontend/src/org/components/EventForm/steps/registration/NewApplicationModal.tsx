import { yupResolver } from '@hookform/resolvers/yup'
import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import {
  Event,
  EventApplication,
  EventApplicationPayload,
} from 'app/services/bisTypes'
import { birthdayValidation, Error, StyledModal } from 'components'
import { useClearPersistentForm, useDirectPersistForm } from 'hooks/persistForm'
import { EventRegistrationForm } from 'pages/EventRegistration/EventRegistrationForm'
import { FC, useState } from 'react'
import { useForm } from 'react-hook-form'
import * as yup from 'yup'
import styles from './NewApplicationModal.module.scss'

interface INewApplicationModalProps {
  open: boolean
  onClose: () => void
  event: Event
}

export const NewApplicationModal: FC<INewApplicationModalProps> = ({
  open,
  onClose,
  event,
}) => {
  const [isSaving, setIsSaving] = useState(false)

  const eventId = event.id
  const [createEventApplication] =
    api.endpoints.createEventApplication.useMutation()

  const clearPersistentData = useClearPersistentForm(
    'registration',
    String(eventId),
  )

  const validationSchema = yup.object().shape({
    first_name: yup.string().required().trim(),
    last_name: yup.string().required().trim(),
    nickname: yup.string().trim(),
    email: yup.string().email().required(),
    phone: yup.string().required(),
    birthday: birthdayValidation.required(),
    close_person: yup.object().shape({
      first_name: yup.string(),
      last_name: yup.string(),
      email: yup.string().email(),
      phone: yup.string(),
    }),
    answers: yup.array().of(
      yup.object({
        is_required: yup.boolean(),
        answer: yup.string().when('is_required', {
          is: true,
          then: schema => schema.required(),
        }),
      }),
    ),
  })

  const methods = useForm<EventApplication>({
    resolver: yupResolver(validationSchema),
    defaultValues: { birthday: '' },
  })
  const { reset } = methods

  const {
    data: eventWeb,
    isError: isEventError,
    error: eventError,
  } = api.endpoints.readWebEvent.useQuery(
    event?.propagation?.is_shown_on_web ? { id: eventId } : skipToken,
  )

  const persist = useDirectPersistForm('registration', String(eventId))
  const [patchEvent] = api.endpoints.updateEvent.useMutation()

  const handleFormSubmit = async (data: EventApplicationPayload) => {
    try {
      setIsSaving(true)
      if (!event.registration) {
        await patchEvent({
          id: eventId,
          event: { registration: { questionnaire: {} } },
        })
      }
      await createEventApplication({
        application: data,
        eventId,
      }).unwrap()
      clearPersistentData()

      onClose()
    } catch (error) {
      persist({ step: 'progress' })
    } finally {
      setIsSaving(false)
    }
  }

  if (!open) return null

  if (isEventError) return <Error error={eventError}></Error>

  return (
    <StyledModal
      open={open}
      onClose={() => {
        onClose()
        reset()
      }}
      title="Nová přihláška"
    >
      <div
        onClick={e => {
          e.stopPropagation()
        }}
        className={styles.content}
      >
        <div className={styles.modalFormBox}>
          <EventRegistrationForm
            id={String(eventId)}
            questionnaire={eventWeb?.registration?.questionnaire ?? undefined}
            onSubmit={handleFormSubmit}
            onCancel={() => {
              onClose()
              clearPersistentData()
            }}
            isSaving={isSaving}
          />
        </div>
      </div>
    </StyledModal>
  )
}
