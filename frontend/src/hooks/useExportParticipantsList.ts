import { useExport } from 'hooks/useExport'

export interface Props {
  eventId: number
  format: 'pdf' | 'xlsx'
}

/**
 * Generate URL of export api endpoint
 */
const getUri = ({ eventId, format }: Props) =>
  `${
    process.env.REACT_APP_API_BASE_URL ?? '/api/'
  }frontend/events/${eventId}/get_participants_list/?formatting=${format}`

/**
 * Generate name of the exported file
 */
const getName = ({ eventId, format }: Props) =>
  `ucastnicka_listina_${eventId}.${format}`

/**
 * Export participants list from api
 * We don't use rtk-query because we don't want to cache the whole file
 */
export const useExportParticipantsList = () => {
  return useExport(getUri, getName)
}
