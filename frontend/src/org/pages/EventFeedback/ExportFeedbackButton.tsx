import { FC, MouseEvent } from 'react'
import { useExportFeedback } from 'hooks/useExportFeedback'
import { Button } from 'components'

export const ExportFeedbackButton: FC<{ eventId: number }> = ({ eventId }) => {
  const [exportFeedback, { isLoading }] = useExportFeedback()

  const handleClick = (event: MouseEvent) => {
    event.preventDefault()
    exportFeedback({ eventId })
  }

  return (
    <Button onClick={handleClick} isLoading={isLoading} secondary>
      Exportovat do excelu
    </Button>
  )
}
