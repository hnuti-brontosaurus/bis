import { WebFeedbackForm } from 'app/services/bis'
import { User } from 'app/services/bisTypes'
import { EventFeedback, Reply } from 'app/services/testApi'
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
import merge from 'lodash/merge'
import { FC } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { validationErrors2Message } from 'utils/validationErrors'
import { Inquiry } from './Inquiry'

const form2payload = ({ replies, ...data }: EventFeedback): EventFeedback => ({
  replies: replies.map(({ reply, ...rest }) => ({
    reply: Array.isArray(reply) ? reply.join(', ') : reply,
    ...rest,
  })),
  ...data,
})

export const EventFeedbackForm: FC<{
  feedbackForm: WebFeedbackForm
  user?: User
  id: number
  onCancel: () => void
  onSubmit: (data: EventFeedback) => void
}> = ({ feedbackForm, user, id, onCancel, onSubmit }) => {
  const persistedData = usePersistentFormData('feedback', String(id))
  const methods = useForm<EventFeedback>({
    defaultValues: merge(
      {},
      {
        name: user && `${user.first_name} ${user.last_name}`,
        email: user?.email,
        replies: [] as Reply[],
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
  const handleSubmit = methods.handleSubmit(
    data => onSubmit(form2payload(data)),
    errors =>
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
            <FormSection header="Dotazník">
              {feedbackForm.inquiries.map((inquiry, index) => (
                <Inquiry key={index} inquiry={inquiry} index={index} />
              ))}
            </FormSection>
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
