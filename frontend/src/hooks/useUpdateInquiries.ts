import { api } from 'app/services/bis'
import { InquiryRead } from 'app/services/bisTypes'
import { isEqual } from 'lodash'
import { Optional } from 'utility-types'

type InquiryType = Optional<InquiryRead, 'id'>

export const useUpdateInquiries = () => {
  const [createInquiry] = api.endpoints.createEventFeedbackInquiry.useMutation()
  const [updateInquiry] = api.endpoints.updateEventFeedbackInquiry.useMutation()
  const [deleteInquiry] = api.endpoints.deleteEventFeedbackInquiry.useMutation()

  return function updateInquiries(
    eventId: number,
    inquiries: InquiryType[],
    initial: InquiryType[],
  ) {
    const inquiriesWithOrder = inquiries.map((inquiry, order) => ({
      ...inquiry,
      order,
    }))

    const createPromises = inquiriesWithOrder
      .filter(inquiry => !inquiry.id)
      .map(inquiry => createInquiry({ eventId, inquiry }).unwrap())

    const updatePromises = inquiriesWithOrder
      .filter(inquiry => inquiry.id)
      .filter(inquiry => {
        const original = initial.find(({ id }) => id === inquiry.id)
        return original && !isEqual(original, inquiry)
      })
      .map(({ id, ...inquiry }) =>
        updateInquiry({ eventId, id: id as number, inquiry }).unwrap(),
      )

    const deletePromises = initial
      .filter(inquiry => inquiry.id)
      .filter(inquiry => !inquiries.find(({ id }) => id === inquiry.id))
      .map(({ id }) => deleteInquiry({ eventId, id: id as number }).unwrap())

    return Promise.all([
      ...createPromises,
      ...updatePromises,
      ...deletePromises,
    ])
  }
}
