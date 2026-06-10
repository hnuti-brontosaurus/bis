import {
  ButtonLink,
  FormInputError,
  FormSection,
  FormSectionGroup,
  FormSubsection,
  FullSizeElement,
  InfoBox,
  RichTextEditor,
} from 'components'
import { form as formTexts } from 'config/static/closeEvent'
import { FC } from 'react'
import { Controller, FormProvider, UseFormReturn } from 'react-hook-form'
import { required } from 'utils/validationMessages'
import { FeedbackStepFormShape } from './CloseEventForm'
import { ExternalHeaderLink } from './ExternalHeaderLink'
import { FeedbackStepInfo } from './FeedbackStepInfo'
import { InquiriesFormSection } from './InquiriesFormSection'

interface Props {
  eventId: number
  firstIndex?: number
  methods: UseFormReturn<FeedbackStepFormShape, any>
  feedbackRequired: boolean
}
export const FeedbackStep: FC<Props> = ({
  firstIndex,
  methods,
  eventId,
  feedbackRequired,
}) => (
  <FormProvider {...methods}>
    <form>
      <FormSectionGroup startIndex={firstIndex}>
        <FormSection
          header="e-mail po akci"
          help="Po akci se automaticky posílá e-mail se zpětnou vazbou. Tady si můžete upravit jeho znění."
        >
          <InfoBox>
            <p>
              {feedbackRequired
                ? 'Zpětná vazba bude po skončení akce automaticky odeslána účastníkům e-mailem.'
                : 'Po skončení akce můžeš účastníkům poslat zpětnou vazbu emailem.'}
              <ExternalHeaderLink href="https://drive.google.com/file/d/1rETo1BiZjOi0wVUUWxoGdQ0yFwxfqTS7/view?usp=sharing">
                Ukázkový email se zpětnou vazbou
              </ExternalHeaderLink>
            </p>
            <p>
              Text e-mailu si můžeš upravit. Proměnná <b>*|nazev_akce|*</b> se
              automaticky nahradí názvem akce a <b>*|osloveni|*</b> jménem
              účastníka. Pokud chceš tyto údaje v e-mailu zachovat, proměnné
              nemaž ani neupravuj.
            </p>
          </InfoBox>
          <FormSubsection header="Předmět e-mailu">
            <FormInputError isBlock>
              <FullSizeElement>
                <input
                  type="text"
                  {...methods.register('feedback_form.email_subject')}
                />
              </FullSizeElement>
            </FormInputError>
          </FormSubsection>
          <FormSubsection header="Text e-mailu">
            <FormInputError isBlock>
              <Controller
                name="feedback_form.email_content"
                control={methods.control}
                render={({ field }) => <RichTextEditor {...field} />}
              />
            </FormInputError>
          </FormSubsection>
        </FormSection>
        <FormSection header="zpětná vazba">
          <FeedbackStepInfo feedbackRequired={feedbackRequired} />
          <FormSubsection
            header="Úvod k dotazníku"
            required
            help={formTexts.feedback_form.introduction.help}
          >
            <FullSizeElement>
              <FormInputError>
                <textarea
                  {...methods.register('feedback_form.introduction', {
                    required,
                  })}
                />
              </FormInputError>
            </FullSizeElement>
          </FormSubsection>
          <FormSubsection header="Text po odeslání" required>
            <FullSizeElement>
              <FormInputError>
                <textarea
                  {...methods.register('feedback_form.after_submit_text', {
                    required,
                  })}
                />
              </FormInputError>
            </FullSizeElement>
          </FormSubsection>
          <InquiriesFormSection />
        </FormSection>
        <InfoBox>
          {feedbackRequired ? (
            <>
              Formulář zpětné akce je k nahlédnutí{' '}
              <ButtonLink to={`/akce/${eventId}/zpetna_vazba`} tertiary>
                zde
              </ButtonLink>{' '}
              (změny je potřeba uložit, aby se projevily).
            </>
          ) : (
            <>
              Formulář zpětné vazby můžeš poslat účastníkům přes tlačítko
              "poslat zpětnou vazbu" a nebo můžeš použít tento odkaz:{' '}
              <ButtonLink to={`/akce/${eventId}/zpetna_vazba`} tertiary>
                {window.location.origin}/akce/{eventId}/zpetna_vazba
              </ButtonLink>
            </>
          )}
        </InfoBox>
      </FormSectionGroup>
    </form>
  </FormProvider>
)
