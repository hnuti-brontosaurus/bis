import { Event } from 'app/services/bisTypes'
import { ReactComponent as Counted } from 'assets/counting.svg'
import { ReactComponent as EmailList } from 'assets/email-list.svg'
import { ReactComponent as FullList } from 'assets/full-list.svg'
import classNames from 'classnames'
import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  IconSelect,
  IconSelectGroup,
  Label,
  NumberInput,
} from 'components'
import { InlineSection } from 'components/FormLayout/FormLayout'
import { useConfirmWithModal } from 'hooks/useConfirmWithModal'
import { ParticipantsStep as ParticipantsList } from 'org/components/EventForm/steps/ParticipantsStep'
import { useEffect } from 'react'
import { Controller, FormProvider, UseFormReturn } from 'react-hook-form'
import { required } from 'utils/validationMessages'
import type {
  CloseEventFormShape,
  ParticipantsStepFormInnerShape,
} from './CloseEventForm'
import styles from './ParticipantsStep.module.scss'
import { SimpleParticipants } from './SimpleParticipants'

type ParticipantInputType =
  CloseEventFormShape['record']['participantInputType']

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
  event: Event
  areParticipantsRequired: boolean
  methods: UseFormReturn<ParticipantsStepFormInnerShape>
}) => {
  const { watch, control, trigger, formState } = methods

  // list of participants is shown when it's required
  // or when organizers prefer it rather than filling just numbers

  const inputType = watch('record.participantInputType')

  useEffect(() => {
    const subscription = watch((values, { name }) => {
      if (formState.isSubmitted && name === 'record.number_of_participants')
        trigger('record.number_of_participants_under_26')
      if (formState.isSubmitted && name === 'record.participantInputType')
        trigger()
    })
    return () => subscription.unsubscribe()
  }, [formState.isSubmitted, trigger, watch])

  const [confirmWithModal] = useConfirmWithModal({
    title: 'Měníš způsob registrace účastníků',
    message:
      'Je možné vybrat pouze jeden způsob registrace. Pokud chceš změnit způsob registrace, data, která jsou zadaná v počtu účastníků a seznamu účastníků, nebudou uložena. Chceš pokračovat?',
  })

  return (
    <FormProvider {...methods}>
      <form>
        {/* orgs should be able to always add people to the participants list
      but when the event group is "other", it's optional, and they must fill number_of_participants instead
      */}
        <FormSectionGroup>
          {!areParticipantsRequired && (
            <FormSection required header="Způsob registrace účastníků">
              <FormInputError name="participantInputType">
                <Controller
                  name="record.participantInputType"
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
                                if (inputType) {
                                  confirmWithModal(() =>
                                    field.onChange(e.target.value),
                                  )
                                } else {
                                  field.onChange(e.target.value)
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
              <SimpleParticipants />
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
