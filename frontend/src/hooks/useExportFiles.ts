import { useExport } from './useExport'

interface Props {
  eventId: number
}

const getUri = ({ eventId }: Props) =>
  `${
    import.meta.env.VITE_API_BASE_URL ?? '/api/'
  }frontend/events/${eventId}/export_files`

export const useExportFiles = () => useExport(getUri)
