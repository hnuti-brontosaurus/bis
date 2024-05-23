import { useExport } from 'org/components/EventForm/steps/registration/useExport'

interface Props {
  eventId: number
}

const getUri = ({ eventId }: Props) =>
  `${
    process.env.REACT_APP_API_BASE_URL ?? '/api/'
  }frontend/events/${eventId}/export_files`

const getName = ({ eventId }: Props) => `fotky_${eventId}.zip`

export const useExportFiles = () => useExport(getUri, getName)
