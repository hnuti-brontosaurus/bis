import { Outlet } from 'react-router-dom'
import { MixedLayout } from './MixedLayout'

export const MixedOutlet = () => {
  return (
    <MixedLayout>
      <Outlet />
    </MixedLayout>
  )
}
