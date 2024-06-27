import { FC } from 'react'
import { FormSection, FormSectionGroup } from 'components'
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
          <QuestionsFormSection name="inquiries" methods={methods} />
        </FormSection>
      </FormSectionGroup>
    </form>
  </FormProvider>
)
