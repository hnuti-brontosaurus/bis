import { useExport } from './useExport'

interface Props {
  eventId: number
}

const getUri = ({ eventId }: Props) =>
  `${
    process.env.REACT_APP_API_BASE_URL ?? '/api/'
  }frontend/events/${eventId}/get_feedbacks/`

const getName = ({ eventId }: Props) => `zpetna_vazba_${eventId}.xlsx`

export const useExportFeedback = () => useExport(getUri, getName)
