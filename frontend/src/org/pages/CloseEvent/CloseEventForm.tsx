import { yupResolver } from '@hookform/resolvers/yup'
import {
  AttendanceListPagePayload,
  EventPhotoPayload,
  Finance,
  FinanceReceipt,
  FullEvent,
  InquiryRead,
  PatchedEvent,
  Record,
} from 'app/services/bisTypes'
import { Step, Steps } from 'components'
import * as translations from 'config/static/combinedTranslations'
import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import {
  useClearPersistentForm,
  usePersistentFormData,
  usePersistForm,
} from 'hooks/persistForm'
import { cloneDeep, mergeWith, omit } from 'lodash'
import merge from 'lodash/merge'
import pick from 'lodash/pick'
import { FieldErrorsImpl, useForm } from 'react-hook-form'
import type { DeepPick } from 'ts-deep-pick'
import { Assign, Optional } from 'utility-types'
import {
  hasFormError,
  isEventVolunteering,
  withOverwriteArray,
} from 'utils/helpers'
import { validationErrors2Message } from 'utils/validationErrors'
import * as yup from 'yup'
import { EvidenceStep } from './EvidenceStep'
import { FeedbackStep } from './FeedbackStep'
import { ParticipantsStep } from './ParticipantsStep'

export type CloseEventPayload = DeepPick<
  PatchedEvent,
  'is_closed' | 'record' | 'finance.bank_account_number'
> & {
  photos: EventPhotoPayload[]
  pages: AttendanceListPagePayload[]
  receipts: Optional<FinanceReceipt, 'id'>[]
  inquiries: Optional<InquiryRead, 'id'>[]
}

// Forms setup
export type EvidenceStepFormShape = {
  record: Pick<
    Record,
    | 'total_hours_worked'
    | 'comment_on_work_done'
    | 'is_event_closed_email_enabled'
  >
  finance: Pick<Finance, 'bank_account_number'>
} & {
  photos: EventPhotoPayload[]
  pages: AttendanceListPagePayload[]
  receipts: Optional<FinanceReceipt, 'id'>[]
}

export type ParticipantsStepFormShape = {
  record: Pick<
    Record,
    | 'participants'
    | 'number_of_participants'
    | 'number_of_participants_under_26'
    | 'contacts'
  >
}

export type ParticipantInputType = 'count' | 'simple-list' | 'full-list'

export type ParticipantsStepFormInnerShape = Assign<
  ParticipantsStepFormShape,
  {
    record: ParticipantsStepFormShape['record'] & {
      participantInputType: ParticipantInputType
    }
  }
>

export type FeedbackStepFormShape = {
  record: Pick<Record, 'feedback_form'>
  inquiries: Optional<InquiryRead, 'id' | 'order'>[]
}

export type CloseEventFormData = EvidenceStepFormShape &
  ParticipantsStepFormShape &
  FeedbackStepFormShape

export type CloseEventFormShape = EvidenceStepFormShape &
  ParticipantsStepFormInnerShape &
  FeedbackStepFormShape

const pickEvidenceData = (data: Partial<CloseEventFormShape>) =>
  pick(
    data,
    'record.total_hours_worked',
    'record.comment_on_work_done',
    'record.is_event_closed_email_enabled',
    'finance.bank_account_number',
    'photos',
    'pages',
    'receipts',
  )

const pickParticipantsData = (data: Partial<CloseEventFormShape>) =>
  pick(
    data,
    //'record.participants',
    'record.number_of_participants',
    'record.number_of_participants_under_26',
    'record.participantInputType',
    'record.contacts',
  )

const pickFeedbackData = (data: Partial<CloseEventFormShape>) =>
  pick(data, 'inquiries', 'record.feedback_form')

const formData2payload = ({
  is_closed,
  ...data
}: CloseEventFormShape & { is_closed: boolean }): CloseEventPayload => {
  const { participantInputType } = data.record
  const payload = cloneDeep(omit(data, 'record.participantInputType'))

  if (participantInputType === 'full-list') {
    payload.record.number_of_participants = null
    payload.record.number_of_participants_under_26 = null
    payload.record.contacts = []
    // participants get saved separately
    // so we don't want to overwrite them with potentially outdated list
    delete payload.record.participants
  } else {
    payload.record.participants = []
  }

  if (payload.finance && !payload.finance.bank_account_number)
    payload.finance.bank_account_number = ''

  return merge(is_closed ? { is_closed: true } : {}, payload)
}

const initialData2form = (
  data: Partial<CloseEventFormData>,
  event: FullEvent,
): Partial<CloseEventFormShape> => {
  let participantInputType: ParticipantInputType | undefined = undefined

  if (event.group.slug === 'other') {
    if (event.record?.participants?.length) {
      participantInputType = 'full-list'
    } else if (
      typeof event.record?.number_of_participants === 'number' &&
      event.record?.contacts &&
      event.record.contacts.length > 0
    ) {
      participantInputType = 'simple-list'
    } else if (typeof event.record?.number_of_participants === 'number') {
      participantInputType = 'count'
    }
  } else {
    participantInputType = 'full-list'
  }

  if (participantInputType) {
    return merge({}, data, { record: { participantInputType } })
  } else return data as Partial<CloseEventFormShape>
}

const validationSchema: yup.ObjectSchema<ParticipantsStepFormInnerShape> =
  yup.object({
    record: yup.object({
      contacts: yup.array(
        yup.object({
          first_name: yup.string().required(),
          last_name: yup.string().required(),
          email: yup.string().email().required(),
          phone: yup.string(),
        }),
      ),
      participantInputType: yup
        .string()
        .oneOf(['full-list', 'simple-list', 'count'])
        .required('Vyberte, prosím, jednu z možností'),
      number_of_participants: yup
        .number()
        .min(0, 'Hodnota musí být větší nebo rovna 0')
        .when('participantInputType', {
          is: (inputType: ParticipantInputType) =>
            inputType === 'simple-list' || inputType === 'count',
          then: schema => schema.required(),
          otherwise: schema => schema.nullable(),
        }),
      number_of_participants_under_26: yup
        .number()
        .min(0, 'Hodnota musí být větší nebo rovna 0')
        .when(
          ['number_of_participants'],
          ([nop]: number[], schema: yup.NumberSchema) =>
            schema.max(
              nop,
              'Hodnota nesmí být větší než počet účastníků celkem',
            ),
        )
        .when('participantInputType', {
          is: (inputType: ParticipantInputType) =>
            inputType === 'simple-list' || inputType === 'count',
          then: schema => schema.required(),
          otherwise: schema => schema.nullable(),
        }),
    }),
  })

export const CloseEventForm = ({
  event,
  initialData,
  onSubmit,
  onCancel,
  id,
}: {
  event: FullEvent
  initialData: Partial<CloseEventFormData>
  onSubmit: (data: CloseEventPayload) => void
  onCancel: () => void
  id: string
}) => {
  // load persisted data
  const savedData = usePersistentFormData('closeEvent', id)
  const initialAndSavedData = merge(
    {},
    initialData2form(initialData, event),
    savedData,
  )

  const evidenceFormMethods = useForm<EvidenceStepFormShape>({
    defaultValues: pickEvidenceData(initialAndSavedData),
  })
  const participantsFormMethods = useForm<ParticipantsStepFormInnerShape>({
    defaultValues: pickParticipantsData(initialAndSavedData),
    resolver: yupResolver(validationSchema),
  })
  const feedbackFormMethods = useForm<FeedbackStepFormShape>({
    defaultValues: pickFeedbackData(initialAndSavedData),
  })
  const { getValues: getValuesParticipants } = participantsFormMethods

  const countEvidenceFirstStep = () => {
    const listType = getValuesParticipants('record.participantInputType')

    if (areParticipantsRequired) {
      return 2
    }
    if (listType === 'simple-list') {
      return 4
    } else if (listType === 'full-list') {
      return 3
    }
    return 3
  }

  const showMessage = useShowMessage()

  usePersistForm(
    'closeEvent',
    id,
    evidenceFormMethods.watch,
    participantsFormMethods.watch,
    feedbackFormMethods.watch,
  )

  const isVolunteering = isEventVolunteering(event)

  // attendance list is required when the event is camp or weekend event
  const areParticipantsRequired = ['camp', 'weekend_event'].includes(
    event.group.slug,
  )
  // but we actually have a field that keeps this info
  // const areParticipantsRequired = event.is_attendance_list_required ?? false

  const handleSubmit = async ({ is_closed }: { is_closed: boolean }) => {
    // let's validate both forms and get data from them
    // then let's send the data to API
    // then let's clear the redux persistent state
    // then redirect to the event page, or event record page, or whatever
    let evidence: EvidenceStepFormShape = {} as EvidenceStepFormShape
    let participants: ParticipantsStepFormInnerShape =
      {} as ParticipantsStepFormInnerShape
    let feedback = {} as FeedbackStepFormShape
    let isValid = true
    let evidenceErrors: FieldErrorsImpl<EvidenceStepFormShape> = {}
    let participantsErrors: FieldErrorsImpl<ParticipantsStepFormInnerShape> = {}
    let feedbackErrors: FieldErrorsImpl<FeedbackStepFormShape> = {}
    await Promise.all([
      evidenceFormMethods.handleSubmit(
        data => {
          evidence = data
        },
        errors => {
          isValid = false
          evidenceErrors = errors
          evidence = evidenceFormMethods.getValues()
        },
      )(),
      participantsFormMethods.handleSubmit(
        data => {
          participants = data
        },
        errors => {
          isValid = false
          participantsErrors = errors
          participants = participantsFormMethods.getValues()
        },
      )(),
      feedbackFormMethods.handleSubmit(
        data => {
          feedback = data
        },
        errors => {
          feedbackErrors = errors
          feedback = feedbackFormMethods.getValues()
        },
      )(),
    ])

    if (is_closed && !isValid) {
      // TODO make nicer
      showMessage({
        type: 'error',
        message: 'Opravte, prosím, chyby ve validaci',
        detail: validationErrors2Message(
          merge({}, evidenceErrors, participantsErrors) as FieldErrorsImpl,
          translations.event,
          translations.generic,
        ),
      })
    } else {
      const data = mergeWith(
        {},
        evidence,
        participants,
        feedback,
        { is_closed },
        {
          photos: evidence?.photos?.filter(photo => photo.photo) || [],
          pages: evidence?.pages?.filter(page => page.page) || [],
          receipts:
            evidence?.receipts?.filter(receipt => receipt.receipt) || [],
        },
        withOverwriteArray,
      )

      if (
        String(data.record.total_hours_worked) === '' ||
        data.record.total_hours_worked === null
      )
        delete data.record.total_hours_worked

      await onSubmit(formData2payload(data))
      clearPersist()
    }
  }

  const clearPersist = useClearPersistentForm('closeEvent', id)

  const handleCancel = () => {
    // evidenceFormMethods.reset(pickEvidenceData(initialData))
    // participantsFormMethods.reset(pickParticipantsData(initialData))
    clearPersist()
    onCancel()
  }

  return (
    <Steps
      onSubmit={handleSubmit}
      onCancel={handleCancel}
      actions={[
        { name: 'uložit', props: { is_closed: false } },
        { name: 'uložit a uzavřít', props: { is_closed: true } },
      ]}
    >
      <Step name="účastníci" hasError={hasFormError(participantsFormMethods)}>
        <ParticipantsStep
          areParticipantsRequired={areParticipantsRequired}
          methods={participantsFormMethods}
          event={event}
        />
      </Step>
      <Step name="práce a další" hasError={hasFormError(evidenceFormMethods)}>
        <EvidenceStep
          eventId={event.id}
          isVolunteering={isVolunteering}
          methods={evidenceFormMethods}
          firstIndex={countEvidenceFirstStep()}
          multipleSubevents={
            !!event.number_of_sub_events && event.number_of_sub_events > 1
          }
        />
      </Step>
      <Step name="zpětná vazba">
        <FeedbackStep
          eventId={event.id}
          methods={feedbackFormMethods}
          firstIndex={countEvidenceFirstStep() + 6}
        />
      </Step>
    </Steps>
  )
}
