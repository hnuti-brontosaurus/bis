import { FC, MouseEvent } from 'react'
import { Button } from 'components'
import { FaDownload } from 'react-icons/fa'
import { useExportFiles } from '../../hooks/useExportFiles'

export const ExportFilesButton: FC<{ eventId: number }> = ({ eventId }) => {
  const [exportFiles, { isLoading }] = useExportFiles()
  const handleClick = (event: MouseEvent) => {
    event.preventDefault()
    exportFiles({ eventId })
  }
  return (
    <Button onClick={handleClick} secondary isLoading={isLoading}>
      <FaDownload /> fotky
    </Button>
  )
}
