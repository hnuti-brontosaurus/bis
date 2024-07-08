import { FC } from 'react'
import { WebFeedbackForm } from 'app/services/bis'

export const EventFeedbackForm: FC<{ feedbackForm: WebFeedbackForm }> = ({
  feedbackForm,
}) => <>{feedbackForm.introduction && <div>{feedbackForm.introduction}</div>}</>
