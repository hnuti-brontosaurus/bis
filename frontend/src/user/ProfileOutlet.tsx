import { api } from 'app/services/bis'
import { Error, Loading } from 'components'
import { Outlet, useParams } from 'react-router-dom'

export const ProfileOutlet = () => {
  const params = useParams()
  const userId = params.userId as string

  const {
    data: user,
    isError,
    error,
  } = api.endpoints.readUser.useQuery({ id: userId })

  if (isError) return <Error error={error}></Error>

  if (!user) return <Loading>Připravujeme data</Loading>

  return <Outlet context={{ user }} />
}
