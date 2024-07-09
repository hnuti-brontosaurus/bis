import { WebFeedbackForm } from 'app/services/bis'
import { User } from 'app/services/bisTypes'
import { EventFeedback } from 'app/services/testApi'
import {
  Actions,
  Button,
  FormInputError,
  FormSection,
  FormSectionGroup,
  InlineSection,
  Label,
} from 'components'
import * as translations from 'config/static/translations'
import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import { usePersistentFormData, usePersistForm } from 'hooks/persistForm'
import { mergeWith } from 'lodash'
import { FC } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { validationErrors2Message } from 'utils/validationErrors'

export const EventFeedbackForm: FC<{
  feedbackForm: WebFeedbackForm
  user?: User
  id: number
  onCancel: () => void
  onSubmit: (data: EventFeedback) => void
}> = ({ feedbackForm, user, id, onCancel, onSubmit }) => {
  const persistedData = usePersistentFormData('feedback', String(id))
  const methods = useForm({
    defaultValues: mergeWith(
      {},
      {
        name: user ? `${user.first_name} ${user.last_name}` : null,
        email: user ? user.email : null,
        replies: [],
      },
      persistedData,
    ),
  })
  const {
    register,
    watch,
    formState: { isSubmitting },
  } = methods

  usePersistForm('feedback', String(id), watch)

  const showMessage = useShowMessage()
  const handleSubmit = methods.handleSubmit(onSubmit, errors =>
    showMessage({
      type: 'error',
      message: 'Opravte, prosím, chyby ve formuláři.',
      detail: validationErrors2Message(errors, {}, translations.generic),
    }),
  )

  return (
    <>
      {feedbackForm.introduction && <div>{feedbackForm.introduction}</div>}
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit} onReset={onCancel}>
          <FormSectionGroup>
            <FormSection header="Osobní údaje">
              <InlineSection>
                <Label>Jméno</Label>
                <FormInputError>
                  <input type="text" {...register('name')} />
                </FormInputError>
              </InlineSection>
              <InlineSection>
                <Label>E-mail</Label>
                <FormInputError>
                  <input type="email" {...register('email')} />
                </FormInputError>
              </InlineSection>
            </FormSection>
            <FormSection header="Dotazník">TODO</FormSection>
          </FormSectionGroup>
          <Actions>
            <Button secondary type="reset">
              Zrušit
            </Button>
            <Button primary type="submit" isLoading={isSubmitting}>
              Odeslat zpětnou vazbu
            </Button>
          </Actions>
        </form>
      </FormProvider>
    </>
  )
}
