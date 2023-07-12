import { Error, Loading } from 'components'
import { useCurrentUser } from 'hooks/currentUser'
import { useReadFullOpportunity } from 'hooks/readFullOpportunity'
import { Outlet, useParams } from 'react-router-dom'

export const OpportunityOutlet = () => {
  const params = useParams()
  const opportunityId = Number(params.opportunityId)
  const { data: user } = useCurrentUser()

  const { data: opportunity, error } = useReadFullOpportunity({
    userId: user!.id,
    id: opportunityId,
  })

  if (error)
    return <Error error={error}>Nepodařilo se nám najít příležitost</Error>

  if (!opportunity) return <Loading>Stahujeme příležitost</Loading>

  return <Outlet context={{ opportunity }} />
}
