import { QuestionType } from 'app/services/bisTypes'
import classNames from 'classnames'
import {
  Button,
  FormInputError,
  FormSection,
  FormSectionGroup,
  FormSubsection,
  FullSizeElement,
  InfoBox,
  InlineSection,
  Label,
} from 'components'
import { form as formTexts } from 'config/static/event'
import { Controller, FormProvider, useFieldArray } from 'react-hook-form'
import { FaPlus, FaTrashAlt } from 'react-icons/fa'
import { requireBoolean } from 'utils/helpers'
import * as messages from 'utils/validationMessages'
import { MethodsShapes } from '..'
import styles from './RegistrationStep.module.scss'

const questionTypes: { type: QuestionType; name: string }[] = [
  { type: 'text', name: 'Odstavec' },
  { type: 'radio', name: 'Výběr z možností' },
  { type: 'checkbox', name: 'Zaškrtávací políčka' },
]

export const RegistrationStep = ({
  methods,
}: {
  methods: MethodsShapes['registration']
}) => {
  const { control, register, watch } = methods
  const questionFields = useFieldArray({
    control,
    name: 'questions',
  })

  const isNotOnWeb = watch('propagation.is_shown_on_web') === false

  return (
    <FormProvider {...methods}>
      <form>
        <FormSectionGroup startIndex={10}>
          <FormSection
            required
            header={formTexts.propagation.is_shown_on_web.name}
            help={formTexts.propagation.is_shown_on_web.help}
          >
            <FormInputError>
              <Controller
                name={'propagation.is_shown_on_web'}
                control={control}
                rules={{ ...requireBoolean }}
                render={({ field }) => (
                  <fieldset>
                    <InlineSection>
                      {[
                        { name: 'Ano', value: true },
                        { name: 'Ne', value: false },
                      ].map(({ name, value }) => (
                        <label key={name} className="radioLabel">
                          <input
                            ref={field.ref}
                            type="radio"
                            name={field.name}
                            id={name}
                            value={String(value)}
                            checked={field.value === value}
                            onChange={e =>
                              field.onChange(
                                e.target.value === 'true'
                                  ? true
                                  : e.target.value === 'false'
                                  ? false
                                  : undefined,
                              )
                            }
                          />{' '}
                          {name}
                        </label>
                      ))}
                    </InlineSection>
                  </fieldset>
                )}
              />
            </FormInputError>
          </FormSection>

          {!isNotOnWeb && (
            <>
              <FormSection
                header="Způsob přihlášení"
                required
                onWeb
                help={formTexts.registrationMethod.help}
              >
                <FormInputError name="registrationMethod">
                  <fieldset>
                    {[
                      {
                        name: 'Standardní přihláška na brontowebu',
                        value: 'standard',
                      },
                      { name: 'Jiná elektronická přihláška', value: 'other' },
                      {
                        name: 'Registrace není potřeba, stačí přijít',
                        value: 'none',
                      },
                      {
                        name: 'Máme bohužel plno, zkuste jinou z našich akcí',
                        value: 'full',
                      },
                    ].map(({ name, value }) => (
                      <label key={value} className="radioLabel">
                        <input
                          type="radio"
                          value={value}
                          id={`registration-method-${value}`}
                          {...register('registrationMethod', {
                            required: messages.required,
                          })}
                        />{' '}
                        {name}
                      </label>
                    ))}
                  </fieldset>
                </FormInputError>
              </FormSection>

              {watch('registrationMethod') === 'other' && (
                <InlineSection>
                  <InfoBox>
                    Opravdu nechcete použít Standardní přihlášku?<br/>
                    Standardní přihláška vám ulehčí práci, zjednoduší přihlašování účastníkům a poskytuje stejné funkce jako google formulář.
                  </InfoBox>
                  <Label required>Odkaz na přihlášku</Label>{' '}
                  <FormInputError>
                    <input
                      type="url"
                      {...register(
                        'registration.alternative_registration_link',
                        {
                          required: messages.required,
                          validate: {
                            url: value => {
                              try {
                                new URL(value as string)
                                return true
                              } catch (e) {
                                return messages.url
                              }
                            },
                          },
                        },
                      )}
                      placeholder="odkaz na vaši přihlášku"
                    />
                  </FormInputError>
                </InlineSection>
              )}

              {/* {watch('registration.is_registration_required') && ( */}
              {watch('registrationMethod') === 'standard' && (
                <FormSubsection
                  header="Přihláška"
                  help={formTexts.registration.questionnaire.help}
                >
                  <FormSubsection
                    header="Úvod k dotazníku"
                    help={
                      formTexts.registration.questionnaire.introduction.help
                    }
                  >
                    <FullSizeElement>
                      <FormInputError>
                        <textarea
                          {...register(
                            'registration.questionnaire.introduction',
                          )}
                        />
                      </FormInputError>
                    </FullSizeElement>
                  </FormSubsection>
                  <FormSubsection
                    header="Text po odeslání"
                    help={
                      formTexts.registration.questionnaire.after_submit_text
                        .help
                    }
                  >
                    <FullSizeElement>
                      <FormInputError>
                        <textarea
                          {...register(
                            'registration.questionnaire.after_submit_text',
                          )}
                        />
                      </FormInputError>
                    </FullSizeElement>
                  </FormSubsection>
                  <FormSubsection
                    header="Otázky"
                    help={
                      'Odstavec = odpověď textem, výběr z možností = při odpovědi na otázku se musí vybrat pouze jedna z možností, zaškrtávací políčka = při odpovědi na otázku je možné vybrat více možností'
                    }
                  >
                    <div className={styles.questionsBox}>
                      <ul className={styles.questionList}>
                        {questionFields.fields.map((item, index) => (
                          <li key={item.id}>
                            <div className={styles.question}>
                              Otázka {index + 1}
                              <div className={styles.questionInputGroup}>
                                <FormInputError
                                  className={styles.questionInput}
                                >
                                  <input
                                    type="text"
                                    {...register(
                                      `questions.${index}.question` as const,
                                      { required: messages.required },
                                    )}
                                  />
                                </FormInputError>
                                <FormInputError className={styles.typeInput}>
                                  <select
                                    {...register(
                                      `questions.${index}.data.type`,
                                      { required: messages.required },
                                    )}
                                  >
                                    {questionTypes.map(({ type, name }) => (
                                      <option key={type} value={type}>
                                        {name}
                                      </option>
                                    ))}
                                  </select>
                                </FormInputError>
                                <label
                                  className={classNames(
                                    'checkboxLabel',
                                    styles.questionRequired,
                                  )}
                                >
                                  <input
                                    type="checkbox"
                                    {...register(
                                      `questions.${index}.is_required` as const,
                                    )}
                                  />{' '}
                                  povinné?
                                </label>
                                <button
                                  type="button"
                                  onClick={() => questionFields.remove(index)}
                                  className={styles.delete}
                                  aria-label="Smazat otázku"
                                  title="Smazat otázku"
                                >
                                  <FaTrashAlt />
                                </button>
                              </div>
                              {['radio', 'checkbox'].includes(
                                watch(`questions.${index}.data.type`),
                              ) && (
                                <QuestionOptions
                                  question={index}
                                  methods={methods}
                                  type={
                                    watch(`questions.${index}.data.type`) as
                                      | 'radio'
                                      | 'checkbox'
                                  }
                                />
                              )}
                            </div>
                          </li>
                        ))}
                        <li>
                          <button
                            className={styles.addQuestionButton}
                            type="button"
                            onClick={() =>
                              questionFields.append({
                                question: '',
                                data: {
                                  type: 'text',
                                  options: [{ option: '' }],
                                },
                              })
                            }
                          >
                            Přidat otázku <FaPlus />
                          </button>
                        </li>
                      </ul>
                    </div>
                  </FormSubsection>
                </FormSubsection>
              )}
            </>
          )}
        </FormSectionGroup>
      </form>
    </FormProvider>
  )
}

const QuestionOptions = ({
  question,
  methods,
  type,
}: {
  question: number
  methods: MethodsShapes['registration']
  type: 'radio' | 'checkbox'
}) => {
  const { control, register } = methods
  const optionFields = useFieldArray({
    control,
    name: `questions.${question}.data.options`,
  })

  return (
    <div>
      <ul
        className={classNames(
          styles.options,
          type === 'radio' ? styles.radio : styles.checkbox,
        )}
      >
        {optionFields.fields.map((item, index) => (
          <li key={item.id}>
            <div className={styles.option}>
              <FormInputError>
                <input
                  {...register(
                    `questions.${question}.data.options.${index}.option`,
                    { required: messages.required },
                  )}
                />
              </FormInputError>
              <button
                type="button"
                onClick={() => optionFields.remove(index)}
                className={styles.delete}
                aria-label="Smazat možnost"
                title="Smazat možnost"
              >
                <FaTrashAlt />
              </button>
            </div>
          </li>
        ))}
        <li>
          <Button
            tertiary
            className={styles.addOptionButton}
            type="button"
            onClick={() => {
              optionFields.append({ option: '' })
            }}
          >
            Přidat možnost <FaPlus />
          </Button>
        </li>
      </ul>
    </div>
  )
}
