import { yupResolver } from '@hookform/resolvers/yup'
import {
  Event,
  EventPhotoPayload,
  AttendanceListPagePayload,
  Finance,
  FinanceReceipt,
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
import { hasFormError, withOverwriteArray } from 'utils/helpers'
import { validationErrors2Message } from 'utils/validationErrors'
import * as yup from 'yup'
import { EvidenceStep } from './EvidenceStep'
import { ParticipantsStep } from './ParticipantsStep'

export type CloseEventPayload = DeepPick<
  PatchedEvent,
  'is_complete' | 'record' | 'finance.bank_account_number'
> & {
  photos: EventPhotoPayload[]
  pages: AttendanceListPagePayload[]
  receipts: Optional<FinanceReceipt, 'id'>[]
}

// Forms setup
export type EvidenceStepFormShape = {
  record: Pick<Record, 'total_hours_worked' | 'comment_on_work_done'>
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

export type CloseEventFormData = EvidenceStepFormShape &
  ParticipantsStepFormShape

export type CloseEventFormShape = EvidenceStepFormShape &
  ParticipantsStepFormInnerShape

const pickEvidenceData = (data: Partial<CloseEventFormShape>) =>
  pick(
    data,
    'record.total_hours_worked',
    'record.comment_on_work_done',
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

const formData2payload = ({
  is_complete,
  ...data
}: CloseEventFormShape & { is_complete: boolean }): CloseEventPayload => {
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

  return merge(is_complete ? { is_complete: true } : {}, payload)
}

const initialData2form = (
  data: Partial<CloseEventFormData>,
  event: Event,
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
  event: Event
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
  )

  const isVolunteering = event.category.slug === 'public__volunteering'

  // attendance list is required when the event is camp or weekend event
  const areParticipantsRequired = ['camp', 'weekend_event'].includes(
    event.group.slug,
  )
  // but we actually have a field that keeps this info
  // const areParticipantsRequired = event.is_attendance_list_required ?? false

  const handleSubmit = async ({ is_complete }: { is_complete: boolean }) => {
    // let's validate both forms and get data from them
    // then let's send the data to API
    // then let's clear the redux persistent state
    // then redirect to the event page, or event record page, or whatever
    let evidence: EvidenceStepFormShape = {} as EvidenceStepFormShape
    let participants: ParticipantsStepFormInnerShape =
      {} as ParticipantsStepFormInnerShape
    let isValid = true
    let evidenceErrors: FieldErrorsImpl<EvidenceStepFormShape> = {}
    let participantsErrors: FieldErrorsImpl<ParticipantsStepFormInnerShape> = {}
    await Promise.all([
      evidenceFormMethods.handleSubmit(
        data => {
          evidence = data
        },
        errors => {
          isValid = false
          evidenceErrors = errors
        },
      )(),
      participantsFormMethods.handleSubmit(
        data => {
          participants = data
        },
        errors => {
          isValid = false
          participantsErrors = errors
        },
      )(),
    ])

    if (isValid) {
      const data = mergeWith(
        {},
        evidence,
        participants,
        { is_complete },
        {
          photos: evidence.photos.filter(photo => photo.photo),
          pages: evidence.pages.filter(page => page.page),
          receipts: evidence.receipts.filter(receipt => receipt.receipt),
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
    } else {
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
        { name: 'uložit', props: { is_complete: false } },
        { name: 'uložit a uzavřít', props: { is_complete: true } },
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
          isVolunteering={isVolunteering}
          methods={evidenceFormMethods}
          firstIndex={countEvidenceFirstStep()}
        />
      </Step>
    </Steps>
  )
}
