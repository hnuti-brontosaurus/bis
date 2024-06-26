import { FC } from 'react'
import { FormSection, FormSectionGroup } from 'components'

interface Props {
  firstIndex?: number
}
export const FeedbackStep: FC<Props> = ({ firstIndex }) => (
  <form>
    <FormSectionGroup startIndex={firstIndex}>
      <FormSection header="zpětná vazba">...</FormSection>
    </FormSectionGroup>
  </form>
)
