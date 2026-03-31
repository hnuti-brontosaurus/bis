import { useAppDispatch } from 'app/hooks'
import debounce from 'lodash/debounce'
import { useMemo } from 'react'

// only last action that is fired, gets dispatched
// after "time (milliseconds)" of inactivity
// this way, we prevent firing too often (with every key stroke etc...)
export const useDebouncedDispatch = (time_ = 300) => {
  const time = (window as any).Cypress ? 0 : time_
  const dispatch = useAppDispatch()
  const debouncedDispatch = useMemo(
    () => debounce(dispatch, time),
    [dispatch, time],
  )
  return debouncedDispatch
}
