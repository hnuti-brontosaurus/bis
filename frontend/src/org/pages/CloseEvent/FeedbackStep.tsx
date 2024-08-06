import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  FormSubsection,
  FullSizeElement,
  InfoBox,
} from 'components'
import { form as formTexts } from 'config/static/closeEvent'
import { QuestionsFormSection } from 'org/components'
import { FC } from 'react'
import { FormProvider, UseFormReturn } from 'react-hook-form'
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
            <InfoBox>
              {formTexts.record.feedback_form.after_submit_text.help}
            </InfoBox>
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
