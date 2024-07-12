import { FC } from 'react'
import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  FormSubsection,
  FullSizeElement,
} from 'components'
import { FormProvider, UseFormReturn } from 'react-hook-form'
import { QuestionsFormSection } from '../../components'
import { FeedbackStepFormShape } from './CloseEventForm'

interface Props {
  firstIndex?: number
  methods: UseFormReturn<FeedbackStepFormShape, any>
}
export const FeedbackStep: FC<Props> = ({ firstIndex, methods }) => (
  <FormProvider {...methods}>
    <form>
      <FormSectionGroup startIndex={firstIndex}>
        <FormSection header="zpětná vazba">
          <FormSubsection header="Úvod k dotazníku">
            <FullSizeElement>
              <FormInputError>
                <textarea
                  {...methods.register('record.feedback_form.introduction')}
                />
              </FormInputError>
            </FullSizeElement>
          </FormSubsection>
          <FormSubsection header="Text po odeslání">
            <FullSizeElement>
              <FormInputError>
                <textarea
                  {...methods.register(
                    'record.feedback_form.after_submit_text',
                  )}
                />
              </FormInputError>
            </FullSizeElement>
          </FormSubsection>
          <QuestionsFormSection
            name="inquiries"
            questionName="inquiry"
            methods={methods}
          />
        </FormSection>
      </FormSectionGroup>
    </form>
  </FormProvider>
)
