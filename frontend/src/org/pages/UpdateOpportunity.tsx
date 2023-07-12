import { api } from 'app/services/bis'
import { Breadcrumbs, Loading, useCreateOrSelectLocation } from 'components'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { useCurrentUser } from 'hooks/currentUser'
import type { FullOpportunity } from 'hooks/readFullOpportunity'
import { useTitle } from 'hooks/title'
import merge from 'lodash/merge'
import { OpportunityForm, OpportunityFormShape } from 'org/components'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'
import { Optional } from 'utility-types'

export const UpdateOpportunity = () => {
  useTitle('Upravit příležitost')
  const params = useParams()
  const opportunityId = Number(params.opportunityId)
  const { data: user } = useCurrentUser()
  const userId = user!.id

  const navigate = useNavigate()

  const showMessage = useShowMessage()

  const { opportunity } = useOutletContext<{ opportunity: FullOpportunity }>()

  const title = `Upravit příležitost ${opportunity?.name ?? ''}`

  useTitle(title)

  const [updateOpportunity, updateOpportunityStatus] =
    api.endpoints.updateOpportunity.useMutation()

  useShowApiErrorMessage(
    updateOpportunityStatus.error,
    'Nepodařilo se upravit příležitost',
  )

  const createOrSelectLocation = useCreateOrSelectLocation()

  if (updateOpportunityStatus.isLoading) {
    return <Loading>Ukládáme změny</Loading>
  }

  const initialData = merge({}, opportunity, {
    category: opportunity.category.id,
    image: opportunity.image.original,
  })

  const handleSubmit = async (
    data: Optional<OpportunityFormShape, 'image'>,
  ) => {
    const locationId = await createOrSelectLocation(data.location)

    // if image hasn't changed, delete it
    if (initialData.image === data.image) delete data.image

    // update opportunity
    await updateOpportunity({
      id: opportunityId,
      userId,
      patchedOpportunity: merge(data, { location: locationId as number }),
    }).unwrap()

    navigate(`/org/prilezitosti/${opportunityId}`)
    showMessage({
      message: 'Příležitost byla úspěšně změněna',
      type: 'success',
    })
  }

  const handleCancel = () => {
    // TODO when form is persistent, remove from persistent storage
    // also ask for confirmation
    navigate('/org/prilezitosti')
  }

  return (
    <>
      <Breadcrumbs opportunityName={opportunity.name} />
      <OpportunityForm
        id={String(userId + '-' + opportunityId)}
        initialData={initialData}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        isUpdate
      />
    </>
  )
}
