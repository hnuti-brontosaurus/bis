import type { EventContact } from 'app/services/bisTypes'
import spreadsheetTemplate from 'assets/templates/vzor_import-ucastniku-z-jednoduche-prezencky.xlsx'
import classNames from 'classnames'
import {
  Button,
  EmptyListPlaceholder,
  ExternalButtonLink,
  FormInputError,
  ImportExcelButton,
  InlineSection,
} from 'components'
import { get } from 'lodash'
import tableStyles from 'org/components/EventForm/steps/ParticipantsStep.module.scss'
import { FormHTMLAttributes, TdHTMLAttributes, useEffect } from 'react'
import { createPortal } from 'react-dom'
import {
  FieldErrors,
  FieldPath,
  FieldValues,
  FormProvider,
  useFieldArray,
  useForm,
  useFormContext,
} from 'react-hook-form'
import { FaCheck, FaTrash } from 'react-icons/fa'
import * as validationMessages from 'utils/validationMessages'
import type { ParticipantsStepFormShape } from './CloseEventForm'
import styles from './SimpleParticipants.module.scss'

const importMap = {
  first_name: 0,
  last_name: 1,
  email: 2,
  phone: 3,
}

export const SimpleParticipants = () => {
  const {
    control,
    register,
    trigger,
    formState: { errors, isSubmitted },
  } = useFormContext<ParticipantsStepFormShape>()
  const peopleFields = useFieldArray({ control, name: 'record.contacts' })

  useEffect(() => {
    if (isSubmitted) trigger('record.contacts')
  }, [isSubmitted, trigger, peopleFields.fields])

  return (
    <div className={styles.container}>
      <div className={styles.importPart}>
        <ImportExcelButton<EventContact>
          keyMap={importMap}
          onUpload={data => peopleFields.append(data)}
        >
          Importovat seznam účastníků z excelu
        </ImportExcelButton>{' '}
        <ExternalButtonLink tertiary href={spreadsheetTemplate}>
          (vzor)
        </ExternalButtonLink>
      </div>
      {/* <div className={classNames(styles.header, styles.userAndExportLine)}>
        Nový účastník:{' '}
      </div> */}

      <div className={styles.inputLine}>
        <SimpleParticipantInput onSubmit={data => peopleFields.prepend(data)} />
      </div>
      <table className={classNames(tableStyles.table, styles.contactTable)}>
        <thead>
          <tr>
            <th>Jméno</th>
            <th>Příjmení</th>
            <th>E-mail</th>
            <th>Telefon</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {peopleFields.fields.map((item, i) => (
            <tr
              key={item.id}
              title={`${item.first_name || '?'} ${item.last_name || '?'}, ${
                item.email || '—'
              }, ${item.phone || '—'}`}
            >
              <TdErr name={`record.contacts.${i}.first_name`} errors={errors}>
                <input {...register(`record.contacts.${i}.first_name`)} />
              </TdErr>
              <TdErr name={`record.contacts.${i}.last_name`} errors={errors}>
                <input {...register(`record.contacts.${i}.last_name`)} />
              </TdErr>
              <TdErr name={`record.contacts.${i}.email`} errors={errors}>
                <input {...register(`record.contacts.${i}.email`)} />
              </TdErr>
              <TdErr name={`record.contacts.${i}.phone`} errors={errors}>
                <input {...register(`record.contacts.${i}.phone`)} />
              </TdErr>
              <td>
                <button type="button" onClick={() => peopleFields.remove(i)}>
                  <FaTrash />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {peopleFields.fields.length === 0 && (
        <div className={styles.emptyTable}>
          <EmptyListPlaceholder label="Nejsou pridani zadne ucastniky" />
        </div>
      )}
    </div>
  )
}
/**
 * table cell capable of displaying error
 */
const TdErr = <T extends FieldValues>({
  name,
  errors,
  ...props
}: TdHTMLAttributes<HTMLTableCellElement> & {
  errors: FieldErrors<T>
  name: FieldPath<T>
}) => (
  <td className={classNames(get(errors, name) ? styles.error : undefined)}>
    {props.children}
    <div className={styles.errorMessage}>
      {get(errors, name)?.message as string}
    </div>
  </td>
)

const SimpleParticipantInput = ({
  formId = 'simple-participant-form',
  defaultValues,
  onSubmit,
}: {
  formId?: string
  defaultValues?: EventContact
  onSubmit: (value: EventContact) => void
}) => {
  const methods = useForm<EventContact>({ defaultValues })
  const { register, handleSubmit, reset, setFocus } = methods

  // change default values
  useEffect(() => {
    if (defaultValues) {
      reset(defaultValues)
    }
  }, [defaultValues, reset, setFocus])

  const handleFormSubmit = handleSubmit(data => {
    onSubmit(data)
    setFocus('first_name')
    reset({ first_name: '', last_name: '', email: '', phone: '' })
  })

  return (
    <>
      <FormProvider {...methods}>
        <OutsideForm id={formId} onSubmit={handleFormSubmit} />
        <InlineSection>
          Nový účastník:
          <FormInputError>
            <input
              form={formId}
              type="text"
              placeholder="Jméno*"
              {...register('first_name', {
                required: validationMessages.required,
              })}
            />
          </FormInputError>
          <FormInputError>
            <input
              form={formId}
              type="text"
              placeholder="Příjmení*"
              {...register('last_name' as const, {
                required: validationMessages.required,
              })}
            />
          </FormInputError>
          <FormInputError>
            <input
              form={formId}
              type="email"
              placeholder="E-mail*"
              {...register('email' as const, {
                required: validationMessages.required,
              })}
            />
          </FormInputError>
          <FormInputError>
            <input
              form={formId}
              type="tel"
              placeholder="Telefon"
              {...register('phone' as const)}
            />
          </FormInputError>
          <Button primary type="submit" form={formId}>
            <FaCheck />
          </Button>
        </InlineSection>
      </FormProvider>
    </>
  )
}

const OutsideForm = ({
  containerId = 'root',
  ...props
}: FormHTMLAttributes<HTMLFormElement> & { containerId?: string }) => {
  const container = document.getElementById(containerId)
  const el = document.createElement('div')

  useEffect(() => {
    if (container) {
      container.appendChild(el)
      return () => {
        container.removeChild(el)
      }
    }
  }, [container, el])

  return createPortal(<form {...props} />, el)
}
