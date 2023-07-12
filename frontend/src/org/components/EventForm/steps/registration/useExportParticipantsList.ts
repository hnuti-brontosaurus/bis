import { useExport } from './useExport'

/**
 * Generate URL of export api endpoint
 */
const getUri = ({ eventId }: { eventId: number }) =>
  `${
    process.env.REACT_APP_API_BASE_URL ?? '/api/'
  }frontend/events/${eventId}/get_participants_list/`

/**
 * Generate name of the exported file
 */
const getName = ({ eventId }: { eventId: number }) =>
  `ucastnicka_listina_${eventId}.xlsx`

/**
 * Export participants list from api
 * We don't use rtk-query because we don't want to cache the whole file
 */
export const useExportParticipantsList = () => {
  return useExport(getUri, getName)
}
