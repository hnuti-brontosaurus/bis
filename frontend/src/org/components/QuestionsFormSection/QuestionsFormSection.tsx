import { QuestionType } from 'app/services/bisTypes'
import classNames from 'classnames'
import { Button, FormInputError, FormSubsection } from 'components'
import { FC } from 'react'
import { useFieldArray, UseFormReturn } from 'react-hook-form'
import { FaPlus, FaTrashAlt } from 'react-icons/fa'
import * as messages from 'utils/validationMessages'
import styles from './QuestionsFormSection.module.scss'

const questionTypes: { type: QuestionType; name: string }[] = [
  { type: 'text', name: 'Odstavec' },
  { type: 'radio', name: 'Výběr z možností' },
  { type: 'checkbox', name: 'Zaškrtávací políčka' },
]

const QuestionOptions: FC<{
  name: string
  question: number
  methods: UseFormReturn
  type: 'checkbox' | 'radio'
}> = ({ name, question, methods, type }) => {
  const { register, control } = methods
  const fields = useFieldArray({
    name: `${name}.${question}.data.options`,
    control,
  })
  return (
    <div>
      <ul
        className={classNames(
          styles.options,
          type === 'radio' ? styles.radio : styles.checkbox,
        )}
      >
        {fields.fields.map((item, index) => (
          <li key={item.id}>
            <div className={styles.option}>
              <FormInputError>
                <input
                  {...register(
                    `${name}.${question}.data.options.${index}.option`,
                    { required: messages.required },
                  )}
                />
              </FormInputError>
              <button
                type="button"
                onClick={() => fields.remove(index)}
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
              fields.append({ option: '' })
            }}
          >
            Přidat možnost <FaPlus />
          </Button>
        </li>
      </ul>
    </div>
  )
}

export const QuestionsFormSection: FC<{
  name: string
  methods: UseFormReturn
}> = ({ name, methods }) => {
  const { control, register, watch } = methods
  const fields = useFieldArray({ name, control })
  return (
    <FormSubsection
      header="Otázky"
      help={
        'Odstavec = odpověď textem, výběr z možností = při odpovědi na otázku se musí vybrat pouze jedna z možností, zaškrtávací políčka = při odpovědi na otázku je možné vybrat více možností'
      }
    >
      <div className={styles.questionsBox}>
        <ul className={styles.questionList}>
          {fields.fields.map((item, index) => (
            <li key={item.id}>
              <div className={styles.question}>
                Otázka {index + 1}
                <div className={styles.questionInputGroup}>
                  <FormInputError className={styles.questionInput}>
                    <input
                      type="text"
                      {...register(`${name}.${index}.question` as const, {
                        required: messages.required,
                      })}
                    />
                  </FormInputError>
                  <FormInputError className={styles.typeInput}>
                    <select
                      {...register(`${name}.${index}.data.type`, {
                        required: messages.required,
                      })}
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
                      {...register(`${name}.${index}.is_required` as const)}
                    />{' '}
                    povinné?
                  </label>
                  <button
                    type="button"
                    onClick={() => fields.remove(index)}
                    className={styles.delete}
                    aria-label="Smazat otázku"
                    title="Smazat otázku"
                  >
                    <FaTrashAlt />
                  </button>
                </div>
                {['radio', 'checkbox'].includes(
                  watch(`${name}.${index}.data.type`),
                ) && (
                  <QuestionOptions
                    name={name}
                    question={index}
                    methods={methods}
                    type={
                      watch(`${name}.${index}.data.type`) as
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
                fields.append({
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
  )
}
