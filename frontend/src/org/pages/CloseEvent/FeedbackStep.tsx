import {
  ButtonLink,
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
import { required } from 'utils/validationMessages'
import { FeedbackStepFormShape } from './CloseEventForm'
import { FeedbackStepInfo } from './FeedbackStepInfo'
import { InquiriesFormSection } from './InquiriesFormSection'

interface Props {
  eventId: number
  firstIndex?: number
  methods: UseFormReturn<FeedbackStepFormShape, any>
}
export const FeedbackStep: FC<Props> = ({ firstIndex, methods, eventId }) => (
  <FormProvider {...methods}>
    <form>
      <FormSectionGroup startIndex={firstIndex}>
        <FormSection header="zpětná vazba">
          <FeedbackStepInfo />
          <FormSubsection
            header="Úvod k dotazníku"
            required
            help={formTexts.record.feedback_form.introduction.help}
          >
            <FullSizeElement>
              <FormInputError>
                <textarea
                  {...methods.register('record.feedback_form.introduction', {
                    required,
                  })}
                />
              </FormInputError>
            </FullSizeElement>
          </FormSubsection>
          <FormSubsection header="Text po odeslání" required>
            <InfoBox>
              {formTexts.record.feedback_form.after_submit_text.help}
            </InfoBox>
            <FullSizeElement>
              <FormInputError>
                <textarea
                  {...methods.register(
                    'record.feedback_form.after_submit_text',
                    { required },
                  )}
                />
              </FormInputError>
            </FullSizeElement>
          </FormSubsection>
          <InquiriesFormSection />
        </FormSection>
        <InfoBox>
          Formulář zpětné vazby najdeš po uložení tohoto formuláře na tomto
          odkazu, který můžeš poslat účastníkům:{' '}
          <ButtonLink to={`/akce/${eventId}/zpetna_vazba`} tertiary>
            {window.location.origin}/akce/{eventId}/zpetna_vazba
          </ButtonLink>
        </InfoBox>
      </FormSectionGroup>
    </form>
  </FormProvider>
)
