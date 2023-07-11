import { yupResolver } from '@hookform/resolvers/yup'
import { WebQuestionnaire } from 'app/services/bis'
import type {
  AnswerPayload,
  EventApplicationPayload,
} from 'app/services/bisTypes'
import { User } from 'app/services/bisTypes'
import classNames from 'classnames'
import {
  Actions,
  BirthdayInput,
  birthdayValidation,
  Button,
  ExternalButtonLink,
  FormInputError,
  FormSection,
  FormSectionGroup,
  FormSubsection,
  InlineSection,
  Label,
} from 'components'
import * as translations from 'config/static/translations'
import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import {
  useClearPersistentForm,
  usePersistentFormData,
  usePersistForm,
} from 'hooks/persistForm'
import { isNil, merge, mergeWith, omit, omitBy, pick } from 'lodash'
import { ApplicationStates } from 'org/components/EventForm/steps/ParticipantsStep'
import { FormEventHandler, MouseEventHandler, useEffect } from 'react'
import {
  Controller,
  FormProvider,
  useFieldArray,
  useForm,
} from 'react-hook-form'
import type { SetNonNullable, SetRequired } from 'type-fest'
import { Assign, Overwrite } from 'utility-types'
import { sortOrder, withOverwriteArray } from 'utils/helpers'
import { validationErrors2Message } from 'utils/validationErrors'
import { required } from 'utils/validationMessages'
import * as yup from 'yup'
import styles from './EventRegistration.module.scss'
import { mergeAnswers } from './helpers'

export type FormAnswer = Overwrite<AnswerPayload, { answer: string | string[] }>

export type RegistrationFormShape = Assign<
  SetRequired<
    SetNonNullable<
      Omit<EventApplicationPayload, 'nickname' | 'health_issues' | 'state'>,
      'first_name' | 'last_name' | 'phone' | 'email' | 'birthday'
    >,
    'birthday' | 'is_child_application'
  >,
  { answers: FormAnswer[] }
>

export type RegistrationFormShapeWithStep = RegistrationFormShape & {
  step: 'progress' | 'finished'
}

const initialData2form = (
  user?: User,
  questionnaire?: WebQuestionnaire,
): Partial<RegistrationFormShape> => {
  const initialPersonalData = user
    ? pick(
        user,
        'first_name',
        'last_name',
        'phone',
        'email',
        'close_person',
        'birthday',
      )
    : undefined

  const initialQuestionnaireData = {
    // we need to clone readonly questions if we want to sort them by their order
    answers: [...(questionnaire?.questions ?? [])].sort(sortOrder)?.map?.(
      question =>
        ({
          question: question.id,
          answer: '',
          is_required: question.is_required,
        } as AnswerPayload),
    ),
  }

  return omitBy(
    merge(
      { close_person: null, is_child_application: false },
      initialPersonalData,
      initialQuestionnaireData,
    ),
    isNil,
  )
}

const form2payload = (data: RegistrationFormShape): EventApplicationPayload => {
  const answers =
    data.answers
      .map(({ answer, question }) => ({
        answer: Array.isArray(answer) ? answer.join(', ') : answer,
        question,
      }))
      .filter(({ answer }) => Boolean(answer)) ?? []

  const submitData = mergeWith(
    {},
    omit(data, 'step'),
    {
      answers,
      address: null,
      close_person: data.is_child_application ? data.close_person : null,
      state: ApplicationStates.pending,
    },
    withOverwriteArray,
  )

  return submitData
}

const validationSchema: yup.ObjectSchema<RegistrationFormShape> = yup.object({
  is_child_application: yup.boolean().defined(),
  first_name: yup.string().trim().required(),
  last_name: yup.string().trim().required(),
  email: yup
    .string()
    .email()
    .when('is_child_application', {
      is: true,
      then: schema => schema.defined(),
      otherwise: schema => schema.required(),
    }),
  phone: yup
    .string()
    .trim()
    .when('is_child_application', {
      is: true,
      then: schema => schema.defined(),
      otherwise: schema => schema.required(),
    }),
  note: yup.string(),
  birthday: birthdayValidation.required(),
  close_person: yup
    .object({
      first_name: yup.string().trim().required(),
      last_name: yup.string().trim().required(),
      phone: yup.string().trim().required(),
      email: yup.string().email().required(),
    })
    .when('is_child_application', {
      is: true,
      then: schema => schema.required(),
      otherwise: schema => schema.notRequired().default(null),
    }),
  answers: yup
    .array()
    .of(
      yup.object({
        question: yup.number().required(),
        is_required: yup.boolean(),
        answer: yup.lazy(val =>
          Array.isArray(val)
            ? yup
                .array()
                .of(yup.string().defined())
                .defined()
                .when('is_required', {
                  is: true,
                  then: schema =>
                    schema.test({
                      message: 'Vyberte alespoň jednu z možností',
                      test: arr => arr.length > 0,
                    }),
                })
            : yup.string().when('is_required', {
                is: true,
                then: schema => schema.required(),
                otherwise: schema => schema.defined(),
              }),
        ),
      }),
    )
    .required(),
})

// May also be called Application instead of Registration
export const EventRegistrationForm = ({
  id,
  questionnaire,
  user,
  onSubmit,
  onCancel,
  isSaving,
}: {
  id: string
  questionnaire?: WebQuestionnaire
  user?: User
  onSubmit: (data: EventApplicationPayload) => void
  onCancel: () => void
  isSaving?: boolean
}) => {
  const persistedData = usePersistentFormData(
    'registration',
    id,
  ) as RegistrationFormShapeWithStep

  const clearPersistentData = useClearPersistentForm('registration', id)
  const defaultValues = mergeWith(
    {},
    initialData2form(user, questionnaire),
    persistedData,
    {
      answers: mergeAnswers(
        questionnaire?.questions ?? [],
        initialData2form(user, questionnaire).answers ?? [],
        persistedData?.answers,
      ),
    },
    withOverwriteArray,
  )

  const methods = useForm<Omit<RegistrationFormShape, 'step'>>({
    resolver: yupResolver(validationSchema),
    defaultValues: defaultValues.is_child_application
      ? defaultValues
      : merge({}, defaultValues, { close_person: null }),
  })

  const {
    register,
    watch,
    handleSubmit,
    control,
    trigger,
    formState,
    setValue,
  } = methods

  usePersistForm('registration', id, watch)

  const showMessage = useShowMessage()

  const handleFormSubmit = handleSubmit(
    async data => {
      await onSubmit(form2payload(data))
    },
    errors => {
      showMessage({
        type: 'error',
        message: 'Opravte, prosím, chyby ve formuláři',
        detail: validationErrors2Message(
          errors,
          {},
          merge({}, translations.generic, {
            answer: translations.answer._name,
          }),
        ),
      })
    },
  )

  const handleCancel: FormEventHandler<HTMLFormElement> = e => {
    e.preventDefault()
    clearPersistentData()
    onCancel()
  }

  const showQuestions = Boolean(
    questionnaire && questionnaire.questions.length > 0,
  )

  const { fields } = useFieldArray({ control, name: 'answers' })

  const is_child_application = watch('is_child_application')

  useEffect(() => {
    if (formState.isSubmitted) trigger()
  }, [formState.isSubmitted, is_child_application, trigger])

  useEffect(() => {
    if (!is_child_application) setValue('close_person', null)
  }, [is_child_application, setValue])

  return (
    <>
      {questionnaire?.introduction && (
        <div className={styles.info}>{questionnaire.introduction}</div>
      )}
      <FormProvider {...methods}>
        <form onSubmit={handleFormSubmit} onReset={handleCancel}>
          <FormSectionGroup>
            <InlineSection>
              <Label>Přihlašuji dítě</Label>
              <FormInputError>
                <input type="checkbox" {...register('is_child_application')} />
              </FormInputError>
            </InlineSection>
            {is_child_application && (
              <FormSection header="Rodič/zákonný zástupce">
                <InlineSection>
                  <Label required>Jméno</Label>
                  <FormInputError>
                    <input
                      type="text"
                      {...register('close_person.first_name')}
                    />
                  </FormInputError>
                </InlineSection>
                <InlineSection>
                  <Label required>Příjmení</Label>
                  <FormInputError>
                    <input
                      type="text"
                      {...register('close_person.last_name')}
                    />
                  </FormInputError>
                </InlineSection>
                <InlineSection>
                  <Label required>Telefon</Label>
                  <FormInputError>
                    <input type="tel" {...register('close_person.phone')} />
                  </FormInputError>
                </InlineSection>
                <InlineSection>
                  <Label required>E-mail</Label>
                  <FormInputError>
                    <input type="email" {...register('close_person.email')} />
                  </FormInputError>
                </InlineSection>
              </FormSection>
            )}
            <FormSection header={is_child_application ? 'Dítě' : 'Osobní data'}>
              <InlineSection>
                <Label required>Jméno</Label>
                <FormInputError>
                  <input type="text" {...register('first_name')} />
                </FormInputError>
              </InlineSection>
              <InlineSection>
                <Label required>Příjmení</Label>
                <FormInputError>
                  <input type="text" {...register('last_name')} />
                </FormInputError>
              </InlineSection>
              <InlineSection>
                <Label required>Datum narození</Label>
                <FormInputError>
                  <Controller
                    control={control}
                    name="birthday"
                    render={({ field }) => <BirthdayInput {...field} />}
                  />
                </FormInputError>
              </InlineSection>
              <InlineSection>
                <Label required={!is_child_application}>Telefon</Label>
                <FormInputError>
                  <input type="tel" {...register('phone')} />
                </FormInputError>
              </InlineSection>
              <InlineSection>
                <Label required={!is_child_application}>E-mail</Label>
                <FormInputError>
                  <input type="email" {...register('email')} />
                </FormInputError>
              </InlineSection>
              <InlineSection>
                <Label>Poznámka</Label>
                <FormInputError>
                  <textarea {...register('note')} />
                </FormInputError>
              </InlineSection>
            </FormSection>
            {showQuestions && (
              <FormSection header="Dotazník">
                {fields.map((field, index) => {
                  const question = questionnaire!.questions[index]
                  if (!question) return null
                  return (
                    <FormSubsection
                      key={field.id}
                      header={question.question}
                      required={question.is_required}
                      headerClassName={styles.questionWordWrap}
                    >
                      <FormInputError name={`answers.${index}.answer`} isBlock>
                        {question.data?.type === 'checkbox' ||
                        question.data?.type === 'radio' ? (
                          <div className={styles.answerBox}>
                            <fieldset
                              className={classNames(styles.questionWordWrap)}
                            >
                              {question.data.options?.map(({ option }) => (
                                <label
                                  key={option}
                                  className={classNames(
                                    styles.questionWordWrap,
                                    `${question.data!.type}Label`,
                                  )}
                                >
                                  <input
                                    type={question.data!.type}
                                    value={option}
                                    {...register(`answers.${index}.answer`, {
                                      required:
                                        question.is_required && required,
                                    })}
                                  />{' '}
                                  {option}
                                </label>
                              ))}
                            </fieldset>
                          </div>
                        ) : (
                          <div className={styles.answerBox}>
                            <textarea
                              {...register(`answers.${index}.answer`, {
                                required: question.is_required && required,
                              })}
                            ></textarea>
                          </div>
                        )}
                      </FormInputError>
                    </FormSubsection>
                  )
                })}
              </FormSection>
            )}
            <InlineSection>
              <Label>
                Odesláním této přihlášky souhlasím se{' '}
                <ExternalButtonLink
                  tertiary
                  href="https://brontosaurus.cz/osobni-udaje"
                  target="__blank"
                  rel="noopener noreferrer"
                  small
                >
                  zpracováním osobních údajů.
                </ExternalButtonLink>
              </Label>
            </InlineSection>
            <Actions>
              <Button secondary type="reset">
                Zrušit
              </Button>
              <Button primary type="submit" isLoading={isSaving}>
                Odeslat přihlášku
              </Button>
            </Actions>
          </FormSectionGroup>
        </form>
      </FormProvider>
    </>
  )
}

export const FinishedStep = ({
  message,
  onFinish,
  onRestart,
}: {
  message: string
  onFinish: MouseEventHandler<HTMLButtonElement>
  onRestart: MouseEventHandler<HTMLButtonElement>
}) => {
  return (
    <div>
      <div className={styles.info}>{message}</div>
      <Actions>
        <Button primary onClick={onFinish}>
          Hotovo!
        </Button>
        <Button primary onClick={onRestart}>
          Přihlásit někoho dalšího
        </Button>
      </Actions>
    </div>
  )
}
