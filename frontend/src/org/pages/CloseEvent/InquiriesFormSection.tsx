import { InquiryType } from 'app/services/bisTypes'
import classNames from 'classnames'
import { Button, FormInputError, FormSubsection } from 'components'
import { FC } from 'react'
import { useFieldArray, useFormContext, useWatch } from 'react-hook-form'
import { FaPlus, FaTrashAlt } from 'react-icons/fa'
import * as messages from 'utils/validationMessages'
import { FeedbackStepFormShape } from './CloseEventForm'
import styles from './InquiryFormSection.module.scss'

const questionTypes: { type: InquiryType; name: string }[] = [
  { type: 'text', name: 'Odstavec' },
  { type: 'radio', name: 'Výběr z možností' },
  { type: 'checkbox', name: 'Zaškrtávací políčka' },
  { type: 'scale', name: 'Škála 1–10' },
  { type: 'header', name: 'Nadpis sekce' },
]

const InquiryOptions: FC<{
  question: number
  type: 'checkbox' | 'radio'
}> = ({ question, type }) => {
  const { register } = useFormContext<FeedbackStepFormShape>()
  const fields = useFieldArray({ name: `inquiries.${question}.data.options` })
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
                    `inquiries.${question}.data.options.${index}.option` as const,
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

const Inquiry: FC<{ index: number; onRemove: () => void }> = ({
  index,
  onRemove,
}) => {
  const { register, watch, setValue } = useFormContext<FeedbackStepFormShape>()
  const inquiryType = useWatch({ name: `inquiries.${index}.data.type` })
  const isHeader = inquiryType === 'header'

  if (isHeader) {
    setValue(`inquiries.${index}.is_required`, false)
  }
  setValue(`inquiries.${index}.data.comment`, inquiryType === 'scale')

  return (
    <li>
      <div className={styles.question}>
        Otázka {index + 1}
        <div className={styles.questionInputGroup}>
          <FormInputError className={styles.questionInput}>
            <input
              type="text"
              {...register(`inquiries.${index}.inquiry` as const, {
                required: messages.required,
              })}
            />
          </FormInputError>
          <FormInputError className={styles.typeInput}>
            <select
              {...register(`inquiries.${index}.data.type` as const, {
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
            className={classNames('checkboxLabel', styles.questionRequired)}
          >
            <input
              type="checkbox"
              {...register(`inquiries.${index}.is_required` as const)}
              disabled={isHeader}
            />{' '}
            povinné?
          </label>
          <button
            type="button"
            onClick={onRemove}
            className={styles.delete}
            aria-label="Smazat otázku"
            title="Smazat otázku"
          >
            <FaTrashAlt />
          </button>
        </div>
        {['radio', 'checkbox'].includes(inquiryType) && (
          <InquiryOptions
            question={index}
            type={inquiryType as 'radio' | 'checkbox'}
          />
        )}
      </div>
    </li>
  )
}

export const InquiriesFormSection: FC = () => {
  const fields = useFieldArray({ name: 'inquiries' })

  return (
    <FormSubsection
      header="Otázky"
      help={
        'Odstavec = odpověď textem, výběr z možností = při odpovědi na otázku se musí vybrat pouze jedna z možností, zaškrtávací políčka = při odpovědi na otázku je možné vybrat více možností, škála 1–10 = výběr na škále 1–10 (zcela splňuje – zcela nesplňuje) s volitelným komentářem, nadpis sekce = vytvoří v dotazníku číslovanou sekci'
      }
    >
      <div className={styles.questionsBox}>
        <ul className={styles.questionList}>
          {fields.fields.map((item, index) => (
            <Inquiry
              key={item.id}
              index={index}
              onRemove={() => fields.remove(index)}
            />
          ))}
          <li>
            <button
              className={styles.addQuestionButton}
              type="button"
              onClick={() =>
                fields.append({
                  inquiry: '',
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
