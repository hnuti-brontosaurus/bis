import { api } from 'app/services/bis'
import { DirectFilesUpload } from 'components'

export const EventPhotos = ({ eventId }: { eventId: number }) => {
  const { data } = api.endpoints.readEventPhotos.useQuery({ eventId })
  const [createPhoto] = api.endpoints.createEventPhoto.useMutation()
  const [deletePhoto] = api.endpoints.deleteEventPhoto.useMutation()

  return (
    <DirectFilesUpload
      name="photos"
      files={data?.results.map(({ id, photo }) => ({
        id,
        url: photo.original,
        preview: photo.small,
      }))}
      upload={photo => createPhoto({ eventId, eventPhoto: { photo } }).unwrap()}
      remove={id => deletePhoto({ eventId, id }).unwrap()}
    />
  )
}

export const AttendanceListPages = ({ eventId }: { eventId: number }) => {
  const { data } = api.endpoints.readAttendanceListPages.useQuery({ eventId })
  const [createPage] = api.endpoints.createAttendanceListPage.useMutation()
  const [deletePage] = api.endpoints.deleteAttendanceListPage.useMutation()

  return (
    <DirectFilesUpload
      name="pages"
      files={data?.results.map(({ id, page }) => ({
        id,
        url: page as string,
      }))}
      upload={page =>
        createPage({ eventId, eventAttendanceListPage: { page } }).unwrap()
      }
      remove={id => deletePage({ eventId, id }).unwrap()}
    />
  )
}

export const FinanceReceipts = ({ eventId }: { eventId: number }) => {
  const { data } = api.endpoints.readFinanceReceipts.useQuery({ eventId })
  const [createReceipt] = api.endpoints.createFinanceReceipt.useMutation()
  const [deleteReceipt] = api.endpoints.deleteFinanceReceipt.useMutation()

  return (
    <DirectFilesUpload
      name="receipts"
      files={data?.results.map(({ id, receipt })=> ({ id, url: receipt }))}
      upload={receipt =>
        createReceipt({ eventId, financeReceipt: { receipt } }).unwrap()
      }
      remove={id => deleteReceipt({ eventId, id }).unwrap()}
    />
  )
}
