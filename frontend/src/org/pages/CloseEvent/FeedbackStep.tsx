import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  FormSubsection,
  FullSizeElement,
  InfoBox,
} from 'components'
import { form as formTexts } from 'config/static/closeEvent'
import { FC } from 'react'
import { FormProvider, UseFormReturn } from 'react-hook-form'
import { FeedbackStepFormShape } from './CloseEventForm'
import { FeedbackStepInfo } from './FeedbackStepInfo'
import { InquiriesFormSection } from './InquiriesFormSection'

interface Props {
  firstIndex?: number
  methods: UseFormReturn<FeedbackStepFormShape, any>
}
export const FeedbackStep: FC<Props> = ({ firstIndex, methods }) => (
  <FormProvider {...methods}>
    <form>
      <FormSectionGroup startIndex={firstIndex}>
        <FormSection header="zpětná vazba">
          <FeedbackStepInfo />
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
          <InquiriesFormSection />
        </FormSection>
      </FormSectionGroup>
    </form>
  </FormProvider>
)
