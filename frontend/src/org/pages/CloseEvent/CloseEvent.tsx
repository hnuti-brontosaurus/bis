import { api } from 'app/services/bis'
import type { Event, EventPayload } from 'app/services/bisTypes'
import { Breadcrumbs, GuideOwl, Loading } from 'components'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { FullEvent } from 'hooks/readFullEvent'
import { useTitle } from 'hooks/title'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'
import { CloseEventForm, CloseEventPayload } from './CloseEventForm'

export const CloseEvent = () => {
  const params = useParams()
  const eventId = Number(params.eventId)
  const navigate = useNavigate()

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

  useShowApiErrorMessage(updateEventError)

  if (!(photos && receipts && pages)) return <Loading>Stahujeme data</Loading>

  const defaultValues = {
    record: event.record ?? undefined,
    photos: photos.results.map(({ photo, ...rest }) => ({
      photo: photo.original,
      ...rest,
    })),
    pages: pages.results,
    finance: event.finance ?? undefined,
    receipts: receipts.results,
  }

  const handleSubmit = async ({
    photos,
    pages,
    receipts,
    ...evidence
  }: CloseEventPayload) => {
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
        createAttendanceListPage({ eventId, eventAttendanceListPage }).unwrap(),
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

    showMessage({
      type: 'success',
      message:
        'Evidence akce byla úspěšně uložena' +
        (evidence.is_complete ? ' a uzavřena' : ''),
    })

    navigate(`/org/akce/${eventId}`)
  }

  const handleCancel = () => {
    navigate(`/org/akce/${eventId}`)
  }

  return (
    <>
      <Breadcrumbs eventName={event && event.name} />

      <CloseEventForm
        id={String(eventId)}
        // we have FullEvent but need just Event
        // let's not bother. we don't need the additional data
        event={event as unknown as Event}
        initialData={defaultValues}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
      />
      <GuideOwl id="po-akce-guide-owl">
        Akce musí být uzavřená (tj. mít kompletně vyplněné údaje po akci) do 20
        dnů od skončení.
      </GuideOwl>
    </>
  )
}
