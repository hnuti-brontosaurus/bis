import { FC, ReactNode } from 'react'
import { Button } from 'components'
import {
  useExportParticipantsList,
  Props as ExportProps,
} from 'hooks/useExportParticipantsList'

export const ExportParticipantsButton: FC<
  ExportProps & {
    children: ReactNode
  }
> = ({ eventId, format, children }) => {
  const [exportParticipants, { isLoading }] = useExportParticipantsList()
  const handleClick = () => exportParticipants({ eventId, format })

  return (
    <Button
      type="button"
      small
      secondary
      onClick={handleClick}
      isLoading={isLoading}
    >
      {children}
    </Button>
  )
}
