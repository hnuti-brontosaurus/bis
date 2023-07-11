import { useLogout } from 'hooks/useLogout'
import { useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'

export const Logout = () => {
  const [searchParams] = useSearchParams()
  const logout = useLogout()

  const next = searchParams.get('next') ?? undefined
  const reload = typeof searchParams.get('reload') === 'string'

  useEffect(() => {
    logout(next, reload)
  }, [logout, next, reload])

  return null
}
