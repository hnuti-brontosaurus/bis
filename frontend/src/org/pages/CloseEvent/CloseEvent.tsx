import { api } from 'app/services/bis'
import type { EventPayload, FullEvent } from 'app/services/bisTypes'
import { Breadcrumbs, GuideOwl, Loading } from 'components'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { useTitle } from 'hooks/title'
import { useUpdateInquiries } from 'hooks/useUpdateInquiries'
import { defaultsDeep, omit } from 'lodash'
import { useState } from 'react'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'
import { sortOrder } from 'utils/helpers'
import { CloseEventForm, CloseEventPayload } from './CloseEventForm'

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

  const updateInquiries = useUpdateInquiries()

  useShowApiErrorMessage(updateEventError)

  if (!(photos && receipts && pages && inquiries))
    return <Loading>Stahujeme data</Loading>

  if (isSubmitting) {
    return <Loading>Ukládáme změny</Loading>
  }

  const defaultValues = {
    record: defaultsDeep(event.record, {
      is_event_closed_email_enabled: true,
    }),
    feedback_form: omit(event.feedback_form, ['sent_at']),
    photos: photos.results.map(({ photo, ...rest }) => ({
      photo: photo.original,
      thumbnail: photo.small,
      ...rest,
    })),
    pages: pages.results,
    finance: event.finance ?? undefined,
    receipts: receipts.results,
    inquiries: inquiries.results.slice().sort(sortOrder),
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

      await Promise.all(
        updateInquiries(eventId, inquiries, defaultValues.inquiries),
      )

      const needsClosing = !evidence.is_closed && !event.is_closed
      const message = `Evidence akce byla úspěšně uložena${
        evidence.is_closed
          ? ' a uzavřena'
          : evidence.feedback_form?.sent_at
          ? ' a zpětná vazba byla odeslána'
          : ''
      }.`
      showMessage({
        type: needsClosing ? 'warning' : 'success',
        message:
          message +
          (needsClosing
            ? ' Nezapomeň akci ještě uzavřít! Akci uzavřeš kliknutím na tlačítko "uložit a uzavřít" do 20 dnů od skončení akce.'
            : ''),
        timeout: event.is_closed ? 5000 : 10_000,
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
