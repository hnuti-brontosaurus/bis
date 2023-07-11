import { api } from 'app/services/bis'
import { User, UserPayload } from 'app/services/bisTypes'
import { Breadcrumbs, Loading, PageHeader } from 'components'
import { UserForm } from 'components/UserForm/UserForm'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { useCurrentUser } from 'hooks/currentUser'
import { useTitle } from 'hooks/title'
import { useState } from 'react'
import { useNavigate, useOutletContext } from 'react-router-dom'

export const EditProfile = () => {
  const { user } = useOutletContext<{ user: User }>()
  const { data: currentUser } = useCurrentUser()
  const navigate = useNavigate()

  const isSelf = currentUser?.id === user.id

  const title = isSelf
    ? 'Upravit můj profil'
    : `Upravit profil uživatele ${user.display_name}`

  useTitle(title)

  const showMessage = useShowMessage()

  const [isSaving, setIsSaving] = useState(false)

  const [updateUser, { error }] = api.endpoints.updateUser.useMutation()

  useShowApiErrorMessage(error)

  const handleSubmit = async (data: UserPayload) => {
    try {
      setIsSaving(true)
      await updateUser({
        id: user.id,
        patchedUser: data,
      }).unwrap()
      showMessage({ type: 'success', message: 'Změny byly úspěšně uloženy' })
      navigate('..')
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    navigate('..')
  }

  if (isSaving) return <Loading>Ukládáme změny</Loading>

  return (
    <>
      <Breadcrumbs userName={user.display_name} />
      <div>
        <PageHeader>{title}</PageHeader>
        <UserForm
          id={user.id}
          isSelf={isSelf}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          initialData={user}
        />
      </div>
    </>
  )
}
