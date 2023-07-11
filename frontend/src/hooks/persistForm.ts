import { useAppDispatch, useAppSelector } from 'app/hooks'
import {
  actions,
  PersistentFormType,
  PersistentFormValue,
  selectFormByTypeAndId,
} from 'features/form/formSlice'
import { useDebouncedDispatch } from 'hooks/debouncedDispatch'
import { useEffect } from 'react'
import { UseFormWatch } from 'react-hook-form'
import { DeepPartial } from 'utility-types'

/**
 * Each persisted form has its type and id,
 * we save, load, and clear its data by the type and id
 */

/**
 * Read persisted form
 * typically to provide as default data when the form is loaded
 *
 * Usage:
 * const persistedData = usePersistentFormData('opportunity', id)
 *
 * // do something with those data...
 */
export const usePersistentFormData = (type: PersistentFormType, id: string) => {
  const savedData = useAppSelector(state =>
    selectFormByTypeAndId(state, type, id),
  )
  return savedData
}

/**
 * Given the type, id, and "watch" from react-hook-forms
 * this hook will save any changes in that form
 *
 * Usage:
 * usePersistForm('opportunity', id, formStep1Methods.watch, formStep2Methods.watch) // etc...
 */
export const usePersistForm = (
  type: PersistentFormType,
  id: string,
  ...watches: UseFormWatch<any>[]
) => {
  const debouncedDispatch = useDebouncedDispatch()

  // whenever the form changes, save it to redux
  // this is to persist the form
  for (const watch of watches) {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    useEffect(() => {
      const subscription = watch(data => {
        debouncedDispatch(
          actions.saveForm({
            id,
            type,
            data,
          }),
        )
      })

      return () => subscription.unsubscribe()
    }, [watch, debouncedDispatch, id, type])
  }
}

/**
 * Given the type and id from react-hook-forms
 * this hook will return method for saving partial form declaratively
 *
 * Usage:
 * const persist = useDirectPersistForm('opportunity', id)
 * persist({ asdf: 'ghjkl' })
 */
export const useDirectPersistForm = (type: PersistentFormType, id: string) => {
  const dispatch = useAppDispatch()
  const persist = (data: DeepPartial<PersistentFormValue<typeof type>>) =>
    dispatch(actions.saveForm({ type, id, data }))
  return persist
}

/**
 * Provided type and id, returns function that removes the persisted data from storage (clears them)
 * However, it doesn't clear the form itself
 *
 * Usage:
 * const clearPersisted = useClearPersistentForm('opportunity', id)
 *
 * handleFormCancel(() => {
 *   // if necessary, do something to clear the form
 *   // ...
 *   // clear persisted storage
 *   clearPersisted()
 *   // and maybe do something in parent element, e.g. redirect
 *   // onCancel()
 * })
 */
export const useClearPersistentForm = (
  type: PersistentFormType,
  id: string,
) => {
  const dispatch = useAppDispatch()
  const clear = () => {
    dispatch(
      actions.removeForm({
        id,
        type,
      }),
    )
  }

  return clear
}
