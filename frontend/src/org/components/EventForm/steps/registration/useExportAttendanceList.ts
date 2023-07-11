import { useExport } from './useExport'

/**
 * Generate URL of export api endpoint
 */
const getUri = ({
  eventId,
  format,
}: {
  eventId: number
  format: 'pdf' | 'xlsx'
}) =>
  `${
    process.env.REACT_APP_API_BASE_URL ?? '/api/'
  }frontend/events/${eventId}/get_attendance_list/?formatting=${format}`

/**
 * Generate name of the exported file
 */
const getName = ({
  eventId,
  format,
}: {
  eventId: number
  format: 'pdf' | 'xlsx'
}) => `prezencni_listina_${eventId}.${format}`

/**
 * Export attendance list from api
 * We don't use rtk-query because we don't want to cache the whole file
 */
export const useExportAttendanceList = () => {
  return useExport(getUri, getName)
}
