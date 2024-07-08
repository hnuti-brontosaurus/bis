import { WebFeedbackForm } from 'app/services/bis'
import { User } from 'app/services/bisTypes'
import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  InlineSection,
  Label,
} from 'components'
import { usePersistentFormData, usePersistForm } from 'hooks/persistForm'
import { mergeWith } from 'lodash'
import { FC } from 'react'
import { FormProvider, useForm } from 'react-hook-form'

export const EventFeedbackForm: FC<{
  feedbackForm: WebFeedbackForm
  user?: User
  id: number
}> = ({ feedbackForm, user, id }) => {
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

  return (
    <>
      {feedbackForm.introduction && <div>{feedbackForm.introduction}</div>}
      <FormProvider {...methods}>
        <form>
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
        </form>
      </FormProvider>
    </>
  )
}
