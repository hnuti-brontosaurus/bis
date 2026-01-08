import { FC, ReactNode } from 'react'
import { Button } from 'components'
import {
  useExportAttendanceList,
  Props as ExportProps,
} from './useExportAttendanceList'

export const ExportAttendanceButton: FC<
  ExportProps & { children: ReactNode }
> = ({ children, eventId, format }) => {
  const [exportAttendance, { isLoading }] = useExportAttendanceList()
  const handleClick = () => exportAttendance({ eventId, format })

  return (
    <Button
      type="button"
      small
      secondary
      isLoading={isLoading}
      onClick={handleClick}
    >
      {children}
    </Button>
  )
}
