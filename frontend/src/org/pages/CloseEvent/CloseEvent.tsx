import { api } from 'app/services/bis'
import type { EventPayload, FullEvent } from 'app/services/bisTypes'
import { Breadcrumbs, GuideOwl, Loading } from 'components'
import { form as formTexts } from 'config/static/closeEvent'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { useTitle } from 'hooks/title'
import { isEqual } from 'lodash'
import { useState } from 'react'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'
import { getRequiredFeedbackInquiries } from 'utils/getRequiredFeedbackInquiries'
import { sortOrder } from 'utils/helpers'
import { CloseEventForm, CloseEventPayload } from './CloseEventForm'
import { defaultsDeep } from 'lodash'

export const CloseEvent = () => {
  const params = useParams()
  const eventId = Number(params.eventId)
  const navigate = useNavigate()

  const [isSubmitting, setSubmitting] = useState(false)

  const { event } = useOutletContext<{ event: FullEvent }>()
  const { data: photos } = api.endpoints.readEventPhotos.useQuery({
    eventId,
  })
  const { data: pages } = api.endpoints.readAttendanceListPages.useQuery({
    eventId,
  })
  const { data: receipts } = api.endpoints.readFinanceReceipts.useQuery({
    eventId,
  })
  const { data: inquiries } = api.endpoints.readEventFeedbackInquiries.useQuery(
    {
      eventId,
      pageSize: 1000, // TODO is there a better way to load all?
    },
  )

  const showMessage = useShowMessage()

  useTitle(event ? `Evidence akce ${event.name}` : 'Evidence akce')

  const [updateEvent, { error: updateEventError }] =
    api.endpoints.updateEvent.useMutation()
  const [createPhoto] = api.endpoints.createEventPhoto.useMutation()
  const [updatePhoto] = api.endpoints.updateEventPhoto.useMutation()
  const [deletePhoto] = api.endpoints.deleteEventPhoto.useMutation()
  const [createAttendanceListPage] =
    api.endpoints.createAttendanceListPage.useMutation()
  const [updateAttendanceListPage] =
    api.endpoints.updateAttendanceListPage.useMutation()
  const [deleteAttendanceListPage] =
    api.endpoints.deleteAttendanceListPage.useMutation()
  const [createReceipt] = api.endpoints.createFinanceReceipt.useMutation()
  const [updateReceipt] = api.endpoints.updateFinanceReceipt.useMutation()
  const [deleteReceipt] = api.endpoints.deleteFinanceReceipt.useMutation()

  const [createInquiry] = api.endpoints.createEventFeedbackInquiry.useMutation()
  const [updateInquiry] = api.endpoints.updateEventFeedbackInquiry.useMutation()
  const [deleteInquiry] = api.endpoints.deleteEventFeedbackInquiry.useMutation()

  useShowApiErrorMessage(updateEventError)

  if (!(photos && receipts && pages && inquiries))
    return <Loading>Stahujeme data</Loading>

  if (isSubmitting) {
    return <Loading>Ukládáme změny</Loading>
  }

  const defaultValues = {
    record: defaultsDeep(event.record, {
      feedback_form: {
        introduction: formTexts.record.feedback_form.introduction.initial,
        after_submit_text:
          formTexts.record.feedback_form.after_submit_text.initial,
      },
      is_event_closed_email_enabled: true,
    }),
    photos: photos.results.map(({ photo, ...rest }) => ({
      photo: photo.original,
      thumbnail: photo.small,
      ...rest,
    })),
    pages: pages.results,
    finance: event.finance ?? undefined,
    receipts: receipts.results,
    inquiries:
      inquiries.results.length > 0
        ? inquiries.results.slice().sort(sortOrder)
        : getRequiredFeedbackInquiries(event),
  }

  const handleSubmit = async ({
    photos,
    pages,
    receipts,
    inquiries,
    ...evidence
  }: CloseEventPayload) => {
    try {
      setSubmitting(true)
      await updateEvent({
        id: eventId,
        event: evidence as Partial<EventPayload>,
      }).unwrap()

      /**
       * Event Photos
       */
      // create each new photo
      const createdPhotoPromises = photos
        // find only new photos...
        .filter(photo => !photo.id)
        // ...and create them via api
        .map(eventPhoto => createPhoto({ eventId, eventPhoto }).unwrap())
      // update each changed photo
      const updatedPhotoPromises = photos
        // find only changed photos...
        .filter(p =>
          Boolean(
            defaultValues.photos.find(
              ({ photo, id }) => id === p.id && photo !== p.photo,
            ),
          ),
        )
        // ...and update them via api
        .map(eventPhoto =>
          updatePhoto({
            eventId,
            id: eventPhoto.id as number,
            patchedEventPhoto: eventPhoto,
          }).unwrap(),
        )
      // delete each removed photo
      const deletedPhotoPromises = defaultValues.photos
        // find all removed photos...
        .filter(p => photos.findIndex(({ id }) => p.id === id) === -1)
        // ...and delete them via api
        .map(({ id }) =>
          deletePhoto({
            eventId,
            id: id as number,
          }).unwrap(),
        )
      // and wait for all the photo api requests to finish
      await Promise.all([
        ...createdPhotoPromises,
        ...updatedPhotoPromises,
        ...deletedPhotoPromises,
      ])

      /**
       * Event Attendance List Pages
       */
      // create each new page
      const createdAttendanceListPagePromises = pages
        // find only new pages...
        .filter(page => !page.id)
        // ...and create them via api
        .map(eventAttendanceListPage =>
          createAttendanceListPage({
            eventId,
            eventAttendanceListPage,
          }).unwrap(),
        )
      // update each changed page
      const updatedAttendanceListPagePromises = pages
        // find only changed pages...
        .filter(p =>
          Boolean(
            defaultValues.pages.find(
              ({ page, id }) => id === p.id && page !== p.page,
            ),
          ),
        )
        // ...and update them via api
        .map(eventAttendanceListPage =>
          updateAttendanceListPage({
            eventId,
            id: eventAttendanceListPage.id as number,
            patchedAttendanceListPage: eventAttendanceListPage,
          }).unwrap(),
        )
      // delete each removed page
      const deletedAttendanceListPagePromises = defaultValues.pages
        // find all removed pages...
        .filter(p => pages.findIndex(({ id }) => p.id === id) === -1)
        // ...and delete them via api
        .map(({ id }) =>
          deleteAttendanceListPage({
            eventId,
            id: id as number,
          }).unwrap(),
        )
      // and wait for all the page api requests to finish
      await Promise.all([
        ...createdAttendanceListPagePromises,
        ...updatedAttendanceListPagePromises,
        ...deletedAttendanceListPagePromises,
      ])

      /**
       * Finance Receipts
       */
      const createdReceiptPromises = receipts
        // find only new receipts...
        .filter(receipt => !receipt.id)
        // ...and create them via api
        .map(financeReceipt =>
          createReceipt({ eventId, financeReceipt }).unwrap(),
        )
      // update each changed receipt
      const updatedReceiptPromises = receipts
        // find only changed receipts...
        .filter(p =>
          Boolean(
            defaultValues.receipts.find(
              ({ receipt, id }) => id === p.id && receipt !== p.receipt,
            ),
          ),
        )
        // ...and update them via api
        .map(financeReceipt =>
          updateReceipt({
            eventId,
            id: financeReceipt.id as number,
            patchedFinanceReceipt: financeReceipt,
          }).unwrap(),
        )
      // delete each removed receipt
      const deletedReceiptPromises = defaultValues.receipts
        // find all removed receipts...
        .filter(p => receipts.findIndex(({ id }) => p.id === id) === -1)
        // ...and delete them via api
        .map(({ id }) =>
          deleteReceipt({
            eventId,
            id: id as number,
          }).unwrap(),
        )
      // and wait for all the receipt api requests to finish
      await Promise.all([
        ...createdReceiptPromises,
        ...updatedReceiptPromises,
        ...deletedReceiptPromises,
      ])

      /**
       * Feedback inquiries
       */
      const inquiriesWithOrder = inquiries.map((inquiry, order) => ({
        ...inquiry,
        order,
      }))
      const createdInquiryPromises = inquiriesWithOrder
        .filter(inquiry => !inquiry.id)
        .map(inquiry => createInquiry({ eventId, inquiry }).unwrap())
      const updateInquiryPromises = inquiriesWithOrder
        .filter(inquiry => inquiry.id)
        .filter(inquiry => {
          const oldInquiry = defaultValues.inquiries.find(
            oi => oi.id === inquiry.id,
          )
          return oldInquiry && !isEqual(oldInquiry, inquiry)
        })
        .map(({ id, ...inquiry }) =>
          updateInquiry({ eventId, id: id as number, inquiry }).unwrap(),
        )
      const deletedInquiryPromises = defaultValues.inquiries
        .filter(inquiry => inquiry.id)
        .filter(inquiry => !inquiries.find(other => other.id === inquiry.id))
        .map(({ id }) => deleteInquiry({ eventId, id: id as number }).unwrap())

      await Promise.all([
        ...createdInquiryPromises,
        ...updateInquiryPromises,
        ...deletedInquiryPromises,
      ])

      showMessage({
        type: evidence.is_closed ? 'success' : 'warning',
        message:
          'Evidence akce byla úspěšně uložena' +
          (evidence.is_closed
            ? ' a uzavřena'
            : '. Nezapomeň akci ještě uzavřít! Akci uzavřeš kliknutím na tlačítko "uložit a uzavřít" do 20 dnů od skončení akce.'),
        timeout: evidence.is_closed ? 5000 : 10_000,
      })

      navigate(`/org/akce/${eventId}`)
    } finally {
      setSubmitting(false)
    }
  }

  const handleCancel = () => {
    navigate(`/org/akce/${eventId}`)
  }

  return (
    <>
      <Breadcrumbs eventName={event && event.name} />

      <CloseEventForm
        id={String(eventId)}
        event={event}
        initialData={defaultValues}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
      />
      <GuideOwl id="po-akce-guide-owl">
        Akce musí být uzavřená (tj. mít kompletně vyplněné povinné údaje po
        akci) do 20 dnů od skončení.
        <br />
        Akci uzavřeš tak, že klikneš na tlačítko "uložit a uzavřít"
      </GuideOwl>
    </>
  )
}
