import { selectAuthenticated } from 'features/auth/authSlice'
import { useSelector } from 'react-redux'

export const useAuth = () => {
  const isAuthenticated = useSelector(selectAuthenticated)

  return isAuthenticated
}
