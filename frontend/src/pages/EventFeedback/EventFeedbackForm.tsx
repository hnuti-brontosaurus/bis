import { WebFeedbackForm } from 'app/services/bis'
import { InquiryRead, User } from 'app/services/bisTypes'
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
import { Assign } from 'utility-types'
import { validationErrors2Message } from 'utils/validationErrors'
import { sortOrder } from 'utils/helpers'
import { Inquiry } from './Inquiry'
import { MessageBox } from './MessageBox'

const form2payload = (
  { replies, ...data }: EventFeedback,
  inquiries: InquiryRead[],
): EventFeedback => ({
  replies: replies
    .filter(reply => !!reply)
    .map(reply => mapReply(reply, inquiries))
    .filter(reply => !!reply.reply),
  ...data,
})

const mapReply = (reply: Reply, inquiries: InquiryRead[]): Reply => {
  const inquiry = inquiries.find(inquiry => reply.inquiry === inquiry.id)

  if (inquiry) {
    switch (inquiry.data?.type) {
      case 'checkbox':
        if (Array.isArray(reply.reply)) {
          return { ...reply, reply: reply.reply.join(', '), value: reply.reply }
        } else {
          return { ...reply, reply: reply.reply, value: [reply.reply] }
        }
      case 'radio':
        return { ...reply, value: [reply.reply] }
      case 'scale':
        return {
          ...reply,
          reply: reply.data?.comment
            ? `${reply.reply} ${reply.data.comment}`
            : reply.reply,
          value: reply.reply,
          data: {
            ...reply.data,
            rating: reply.reply,
          },
        }
      default:
        return reply
    }
  } else {
    return reply
  }
}

interface InquirySection {
  header: string
  inquiries: InquiryRead[]
}

const groupInquiriesByHeaders = (
  inquiries: InquiryRead[],
): InquirySection[] => {
  const sections: InquirySection[] = []
  for (const inquiry of inquiries) {
    if (inquiry.data?.type === 'header') {
      sections.push({
        header: inquiry.inquiry,
        inquiries: [],
      })
    } else {
      sections[sections.length - 1].inquiries.push(inquiry)
    }
  }
  return sections
}

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
        user: user?.id,
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

  console.log(feedbackForm.inquiries)

  const showMessage = useShowMessage()
  const handleSubmit = methods.handleSubmit(
    data => onSubmit(form2payload(data, feedbackForm.inquiries)),
    errors =>
      showMessage({
        type: 'error',
        message: 'Opravte, prosím, chyby ve formuláři.',
        detail: validationErrors2Message(
          errors,
          Object.fromEntries(
            feedbackForm.inquiries.map(inquiry => [
              `replies.${inquiry.id}.reply`,
              inquiry.inquiry,
            ]),
          ),
          translations.generic,
        ),
      }),
  )

  const orderedInquiries = feedbackForm.inquiries.slice().sort(sortOrder)

  return (
    <>
      {feedbackForm.introduction && (
        <MessageBox>{feedbackForm.introduction}</MessageBox>
      )}
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
            {groupInquiriesByHeaders(orderedInquiries).map(
              ({ header, inquiries }) => (
                <FormSection header={header}>
                  {inquiries.map((inquiry, index) => (
                    <Inquiry key={index} inquiry={inquiry} index={inquiry.id} />
                  ))}
                </FormSection>
              ),
            )}
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
