import { FC } from 'react'
import { InquiryRead } from 'app/services/bisTypes'
import { EventFeedbackRead } from 'app/services/testApi'
import styles from './EventFeedbackTable.module.scss'

export const EventFeedbackTable: FC<{
  inquiries: InquiryRead[]
  feedbacks: EventFeedbackRead[]
  onRowClick: (id: number) => void
}> = ({ inquiries, feedbacks, onRowClick }) => (
  <div className={styles.container}>
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Jméno</th>
          <th>E-mail</th>
          {inquiries
            .filter(inquiry => inquiry.data?.type !== 'header')
            .map(({ inquiry, id }) => (
              <th key={id}>{inquiry}</th>
            ))}
        </tr>
      </thead>
      <tbody>
        {feedbacks.map(feedback => (
          <tr key={feedback.id}>
            <td onClick={() => onRowClick(feedback.id)}>{feedback.name}</td>
            <td onClick={() => onRowClick(feedback.id)}>{feedback.email}</td>
            {inquiries
              .filter(inquiry => inquiry.data?.type !== 'header')
              .map(({ id }) => (
                <td key={id} onClick={() => onRowClick(feedback.id)}>
                  {
                    feedback.replies.find(({ inquiry }) => inquiry.id === id)
                      ?.reply
                  }
                </td>
              ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
)
