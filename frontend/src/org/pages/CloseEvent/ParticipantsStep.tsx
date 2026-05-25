import { useAppDispatch } from 'app/hooks'
import { api } from 'app/services/bis'
import { FullEvent } from 'app/services/bisTypes'
import Counted from 'assets/counting.svg?react'
import EmailList from 'assets/email-list.svg?react'
import FullList from 'assets/full-list.svg?react'
import classNames from 'classnames'
import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  IconSelect,
  IconSelectGroup,
  InfoBox,
  Label,
  NumberInput,
} from 'components'
import { InlineSection } from 'components/FormLayout/FormLayout'
import { useShowApiErrorMessage } from 'features/systemMessage/useSystemMessage'
import { useConfirmWithModal } from 'hooks/useConfirmWithModal'
import { ParticipantsStep as ParticipantsList } from 'org/components/EventForm/steps/ParticipantsStep'
import { useEffect } from 'react'
import { Controller, FormProvider, UseFormReturn } from 'react-hook-form'
import { required } from 'utils/validationMessages'
import type {
  CloseEventFormShape,
  ParticipantsStepFormShape,
} from './CloseEventForm'
import styles from './ParticipantsStep.module.scss'
import { SimpleParticipants } from './SimpleParticipants'

type ParticipantInputType = NonNullable<
  CloseEventFormShape['record']['attendance_list_type']
>

const optionButtonConfig: {
  [key: string]: {
    id: ParticipantInputType
    help: string
    text: string
    icon: React.FunctionComponent<React.SVGProps<SVGSVGElement>>
  }
} = {
  count: {
    id: 'count',
    help: 'help1',
    text: 'Mám jen počet účastníků',
    icon: Counted,
  },
  'simple-list': {
    id: 'simple-list',
    help: 'help2',
    text: 'Mám jen jméno + příjmení + email',
    icon: EmailList,
  },
  'full-list': {
    id: 'full-list',
    help: 'help3',
    text: 'Mám všechny informace',
    icon: FullList,
  },
}

export const ParticipantsStep = ({
  event,
  areParticipantsRequired,
  methods,
}: {
  event: FullEvent
  areParticipantsRequired: boolean
  methods: UseFormReturn<ParticipantsStepFormShape>
}) => {
  const { watch, control, trigger, formState, setValue } = methods

  // list of participants is shown when it's required
  // or when organizers prefer it rather than filling just numbers

  const inputType = watch('record.attendance_list_type')

  useEffect(() => {
    const subscription = watch((values, { name }) => {
      if (formState.isSubmitted && name === 'record.number_of_participants')
        trigger('record.number_of_participants_under_26')
      if (formState.isSubmitted && name === 'record.attendance_list_type')
        trigger()
    })
    return () => subscription.unsubscribe()
  }, [formState.isSubmitted, trigger, watch])

  const [confirmWithModal] = useConfirmWithModal({
    title: 'Měníš způsob registrace účastníků',
    message:
      'Je možné vybrat pouze jeden způsob registrace. Pokud chceš změnit způsob registrace, data, která jsou zadaná v počtu účastníků a seznamu účastníků, nebudou uložena. Chceš pokračovat?',
  })

  const [updateEvent, updateEventStatus] =
    api.endpoints.updateEvent.useMutation()
  useShowApiErrorMessage(updateEventStatus.error)
  const dispatch = useAppDispatch()

  // Changing the type wipes the participant list and count fields
  // (server-side and locally) before the new view mounts — counts from
  // the previous mode shouldn't carry over into the new one, and the
  // full-list view would crash on the simple-list projection.
  const switchInputType = async (
    newType: ParticipantInputType,
    apply: () => void,
  ) => {
    await updateEvent({
      id: event.id,
      event: {
        record: {
          participants: [],
          attendance_list_type: newType,
          number_of_participants: null,
          number_of_participants_under_26: null,
        },
      },
    }).unwrap()
    setValue('record.number_of_participants', null)
    setValue('record.number_of_participants_under_26', null)
    // Clear the cached participants synchronously so the about-to-mount
    // full-list view doesn't briefly render against the previous shape
    // while the invalidation-triggered refetch is in flight.
    dispatch(
      api.util.updateQueryData(
        'readEventParticipants',
        { eventId: event.id },
        draft => {
          draft.count = 0
          draft.next = null
          draft.previous = null
          draft.results = []
        },
      ),
    )
    apply()
  }

  return (
    <FormProvider {...methods}>
      <form>
        {/* orgs should be able to always add people to the participants list
      but when the event group is "other", it's optional, and they must fill number_of_participants instead
      */}
        <FormSectionGroup>
          {!areParticipantsRequired && (
            <FormSection required header="Způsob registrace účastníků">
              <FormInputError name="attendance_list_type">
                <Controller
                  name="record.attendance_list_type"
                  control={control}
                  rules={{ required }}
                  render={({ field }) => (
                    <IconSelectGroup>
                      {Object.values(optionButtonConfig).map(
                        ({ id, icon, text }) => {
                          return (
                            <IconSelect
                              key={id}
                              title={'dzik'}
                              text={text}
                              icon={icon}
                              id={id.toString()}
                              ref={field.ref}
                              name={field.name}
                              value={id}
                              checked={id === field.value}
                              onChange={e => {
                                const newType = e.target
                                  .value as ParticipantInputType
                                const apply = () => field.onChange(newType)
                                if (inputType) {
                                  confirmWithModal(() =>
                                    switchInputType(newType, apply),
                                  )
                                } else {
                                  switchInputType(newType, apply)
                                }
                              }}
                            />
                          )
                        },
                      )}
                    </IconSelectGroup>
                  )}
                />
              </FormInputError>

              {inputType && (
                <div className={classNames(styles.changeEvedenceNavigation)}>
                  <div className={styles.textPart}></div>
                </div>
              )}
            </FormSection>
          )}

          {!areParticipantsRequired &&
            (inputType === 'count' || inputType === 'simple-list') && (
              <div>
                <FormSection required header="Počet účastníků">
                  {event.number_of_sub_events &&
                    event.number_of_sub_events > 1 && (
                      <InfoBox>
                        Tato akce je zadaná jako opakovaná. Zadejte tedy celkový
                        počet všech účastníků, kteří se opakovaných akcí
                        účastnili. Např. pokud se akce opakuje 3x s průměrnou
                        účastí 10 lidí, pak je počet účastníků 30.
                      </InfoBox>
                    )}
                  <InlineSection>
                    <Label required>
                      Počet účastníků celkem (včetně organizátorů)
                    </Label>
                    <FormInputError>
                      <Controller
                        control={control}
                        name="record.number_of_participants"
                        render={({ field }) => (
                          <NumberInput
                            {...field}
                            min={0}
                            name="record.number_of_participants"
                          ></NumberInput>
                        )}
                      />
                    </FormInputError>
                  </InlineSection>
                  <InlineSection>
                    <Label required>
                      Z toho počet účastníků do 26 let (včetně organizátorů)
                    </Label>
                    <FormInputError>
                      <Controller
                        control={control}
                        name="record.number_of_participants_under_26"
                        render={({ field }) => (
                          <NumberInput
                            {...field}
                            min={0}
                            name="record.number_of_participants_under_26"
                          ></NumberInput>
                        )}
                      />
                    </FormInputError>
                  </InlineSection>
                </FormSection>
              </div>
            )}

          {!areParticipantsRequired && inputType === 'simple-list' && (
            <FormSection required header="Seznam účastníků">
              <SimpleParticipants eventId={event.id} />
            </FormSection>
          )}
          {(areParticipantsRequired || inputType === 'full-list') && (
            <FormSection required header="Seznam účastníků">
              <ParticipantsList event={event} />
            </FormSection>
          )}
        </FormSectionGroup>
      </form>
    </FormProvider>
  )
}
