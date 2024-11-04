import { FC } from 'react'
import { EventFeedbackRead } from 'app/services/testApi'

export const FeedbackDetail: FC<{
  feedback: EventFeedbackRead
}> = ({ feedback }) => (
  <>
    <div>Jméno: {feedback.name ?? '(nevyplněno)'}</div>
    <div>E-mail: {feedback.email ?? '(nevyplněn)'}</div>
    {feedback.replies.map(reply => (
      <div key={reply.inquiry.id}>
        <h4>{reply.inquiry.inquiry}</h4>
        {reply.reply}
      </div>
    ))}
  </>
)
