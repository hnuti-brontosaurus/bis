import { FC } from 'react'
import { WebFeedbackForm } from 'app/services/bis'
import { FormProvider, useForm } from 'react-hook-form'
import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  InlineSection,
  Label,
} from 'components'

export const EventFeedbackForm: FC<{ feedbackForm: WebFeedbackForm }> = ({
  feedbackForm,
}) => {
  const methods = useForm()
  const { register } = methods
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
