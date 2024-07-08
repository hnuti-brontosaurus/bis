import { WebFeedbackForm } from 'app/services/bis'
import { User } from 'app/services/bisTypes'
import {
  Actions,
  Button,
  FormInputError,
  FormSection,
  FormSectionGroup,
  InlineSection,
  Label,
} from 'components'
import {
  useClearPersistentForm,
  usePersistentFormData,
  usePersistForm,
} from 'hooks/persistForm'
import { mergeWith } from 'lodash'
import { FC } from 'react'
import { FormProvider, useForm } from 'react-hook-form'

export const EventFeedbackForm: FC<{
  feedbackForm: WebFeedbackForm
  user?: User
  id: number
  onCancel: () => void
}> = ({ feedbackForm, user, id, onCancel }) => {
  const persistedData = usePersistentFormData('feedback', String(id))
  const methods = useForm({
    defaultValues: mergeWith(
      {},
      {
        name: user ? `${user.first_name} ${user.last_name}` : null,
        email: user ? user.email : null,
      },
      persistedData,
    ),
  })
  const { register, watch } = methods

  usePersistForm('feedback', String(id), watch)
  const clearPersistentData = useClearPersistentForm('feedback', String(id))

  const handleCancel = () => {
    // TODO prevent default?
    clearPersistentData()
    onCancel()
  }

  return (
    <>
      {feedbackForm.introduction && <div>{feedbackForm.introduction}</div>}
      <FormProvider {...methods}>
        <form onReset={handleCancel}>
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
            <Button primary type="submit">
              Odeslat zpětnou vazbu
            </Button>
          </Actions>
        </form>
      </FormProvider>
    </>
  )
}
