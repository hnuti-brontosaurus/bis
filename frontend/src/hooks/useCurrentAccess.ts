import { useAppDispatch, useAppSelector } from 'app/hooks'
import { actions, selectCurrentAccess } from 'features/auth/authSlice'
import { AccessSlug } from 'utils/roles'

export const useCurrentAccess = () => {
  const access = useAppSelector(selectCurrentAccess)
  const dispatch = useAppDispatch()
  const setAccess = (access: AccessSlug) => dispatch(actions.setAccess(access))
  const setInitialAccess = (access: AccessSlug) =>
    dispatch(actions.setInitialAccess(access))

  return [access, setAccess, setInitialAccess] as const
}
