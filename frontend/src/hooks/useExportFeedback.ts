import { useExport } from './useExport'

interface Props {
  eventId: number
}

const getUri = ({ eventId }: Props) =>
  `${
    import.meta.env.VITE_API_BASE_URL ?? '/api/'
  }frontend/events/${eventId}/get_feedbacks/`

export const useExportFeedback = () => useExport(getUri)
