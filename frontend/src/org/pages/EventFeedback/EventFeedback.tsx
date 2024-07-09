import { FC } from 'react'
import { Breadcrumbs, Loading } from 'components'
import { useOutletContext } from 'react-router-dom'
import { FullEvent } from 'app/services/bisTypes'
import { api } from 'app/services/bis'

export const EventFeedback: FC = () => {
  const { event } = useOutletContext<{ event: FullEvent }>()
  const { data: feedbacks } = api.endpoints.readEventFeedbacks.useQuery({
    eventId: event.id,
  })
  const { data: inquiries } = api.endpoints.readEventFeedbackInquiries.useQuery(
    { eventId: event.id },
  )

  return (
    <>
      <Breadcrumbs eventName={event.name} />
      {feedbacks && feedbacks.results && inquiries && inquiries.results ? (
        <table>
          <thead>
            <tr>
              <th>Jméno</th>
              <th>E-mail</th>
              {inquiries.results.map(({ inquiry }) => (
                <th>{inquiry}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {feedbacks.results.map(feedback => (
              <tr>
                <td>{feedback.name}</td>
                <td>{feedback.email}</td>
                {inquiries.results.map(inquiry => (
                  <td>
                    {
                      feedback.replies.find(
                        reply => inquiry.id === reply.inquiry.id,
                      )?.reply
                    }
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <Loading>Nahráváme zpětnou vazbu</Loading>
      )}
    </>
  )
}
