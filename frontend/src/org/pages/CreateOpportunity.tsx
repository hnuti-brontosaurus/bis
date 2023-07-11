import { api } from 'app/services/bis'
import { Breadcrumbs, Loading, useCreateOrSelectLocation } from 'components'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { useCurrentUser } from 'hooks/currentUser'
import { useTitle } from 'hooks/title'
import merge from 'lodash/merge'
import { OpportunityForm, OpportunityFormShape } from 'org/components'
import { useNavigate } from 'react-router-dom'

export const CreateOpportunity = () => {
  useTitle('Nová příležitost')
  const { data: currentUser } = useCurrentUser()

  const navigate = useNavigate()
  const showMessage = useShowMessage()

  const [createOpportunity, createOpportunityStatus] =
    api.endpoints.createOpportunity.useMutation()
  const createOrSelectLocation = useCreateOrSelectLocation()

  useShowApiErrorMessage(
    createOpportunityStatus.error,
    'Nepodařilo se vytvořit příležitost',
  )

  if (createOpportunityStatus.isLoading) {
    return <Loading>Ukládáme příležitost</Loading>
  }

  const handleSubmit = async (data: OpportunityFormShape) => {
    const locationId = await createOrSelectLocation(data.location)

    const { id } = await createOpportunity({
      userId: currentUser!.id,
      opportunity: merge({}, data, { location: locationId }),
    }).unwrap()
    navigate(`/org/prilezitosti/${id}`)
    showMessage({
      message: 'Příležitost byla úspěšně vytvořena',
      type: 'success',
    })
  }

  const handleCancel = () => {
    // TODO do whatever we need to do to clear the form, when it's persistent
    // perhaps also ask for a confirmation
    navigate('/org/prilezitosti')
  }

  return (
    <div>
      <Breadcrumbs />
      <OpportunityForm
        id="new"
        onSubmit={handleSubmit}
        onCancel={handleCancel}
      />
    </div>
  )
}
