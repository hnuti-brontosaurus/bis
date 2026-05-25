import { api } from 'app/services/bis'
import type { SimpleParticipantPayload } from 'app/services/bisTypes'
import spreadsheetTemplate from 'assets/templates/vzor_import-ucastniku-z-jednoduche-prezencky.xlsx'
import classNames from 'classnames'
import {
  Button,
  EmptyListPlaceholder,
  ExternalButtonLink,
  FormInputError,
  ImportExcelButton,
  InlineSection,
  Loading,
} from 'components'
import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import tableStyles from 'org/components/EventForm/steps/ParticipantsStep.module.scss'
import { FormHTMLAttributes, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { FormProvider, useForm } from 'react-hook-form'
import { FaCheck, FaTrash } from 'react-icons/fa'
import * as validationMessages from 'utils/validationMessages'
import styles from './SimpleParticipants.module.scss'

const importMap = {
  first_name: 0,
  last_name: 1,
  email: 2,
  phone: 3,
}

export const SimpleParticipants = ({ eventId }: { eventId: number }) => {
  const { data: participants, isLoading } =
    api.endpoints.readEventParticipants.useQuery({ eventId })

  const [createSimpleParticipant] =
    api.endpoints.createSimpleParticipant.useMutation()
  const [removeEventParticipant] =
    api.endpoints.removeEventParticipant.useMutation()
  const showMessage = useShowMessage()

  const addParticipants = async (toAdd: SimpleParticipantPayload[]) => {
    if (toAdd.length === 0) return
    try {
      await Promise.all(
        toAdd.map(participant =>
          createSimpleParticipant({ eventId, participant }).unwrap(),
        ),
      )
    } catch {
      showMessage({
        type: 'error',
        message:
          toAdd.length === 1
            ? 'Nepodařilo se přidat účastníka'
            : 'Nepodařilo se přidat některé účastníky',
      })
    }
  }

  const removeParticipant = async (userId: string) => {
    try {
      await removeEventParticipant({ eventId, userId }).unwrap()
    } catch {
      showMessage({
        type: 'error',
        message: 'Nepodařilo se odebrat účastníka',
      })
    }
  }

  if (isLoading) return <Loading>Načítáme účastníky</Loading>

  return (
    <div className={styles.container}>
      <div className={styles.importPart}>
        <ImportExcelButton<SimpleParticipantPayload>
          keyMap={importMap}
          onUpload={addParticipants}
        >
          Importovat seznam účastníků z excelu
        </ImportExcelButton>{' '}
        <ExternalButtonLink tertiary href={spreadsheetTemplate}>
          (vzor)
        </ExternalButtonLink>
      </div>

      <div className={styles.inputLine}>
        <SimpleParticipantInput onSubmit={p => addParticipants([p])} />
      </div>

      <table className={classNames(tableStyles.table, styles.participantTable)}>
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
          {participants?.results.map(p => {
            // Backend masks first_name/last_name/phone for users the
            // current organizer can't see via the standard User filter,
            // so an empty first_name marks a "real BIS user we can't
            // expose here" — show a placeholder instead of blank cells.
            const masked = !p.first_name
            const placeholder = 'uloženo v BISu'
            return (
              <tr
                key={p.id}
                title={
                  masked
                    ? `${placeholder}, ${p.email}`
                    : `${p.first_name} ${p.last_name}, ${p.email}, ${p.phone || '—'}`
                }
              >
                <td>{masked ? placeholder : p.first_name}</td>
                <td>{masked ? placeholder : p.last_name}</td>
                <td>{p.email}</td>
                <td>{masked ? placeholder : p.phone}</td>
                <td>
                  <button type="button" onClick={() => removeParticipant(p.id)}>
                    <FaTrash />
                  </button>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      {!participants?.results.length && (
        <div className={styles.emptyTable}>
          <EmptyListPlaceholder label="Nejsou přidáni žádní účastníci" />
        </div>
      )}
    </div>
  )
}

const SimpleParticipantInput = ({
  formId = 'simple-participant-form',
  defaultValues,
  onSubmit,
}: {
  formId?: string
  defaultValues?: SimpleParticipantPayload
  onSubmit: (value: SimpleParticipantPayload) => void
}) => {
  const methods = useForm<SimpleParticipantPayload>({ defaultValues })
  const { register, handleSubmit, reset, setFocus } = methods

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
