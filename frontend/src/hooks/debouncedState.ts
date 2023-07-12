import debounce from 'lodash/debounce'
import { useEffect, useMemo, useState } from 'react'

export function useDebouncedState<T>(delay: number, defaultValue: T) {
  const [value, setState] = useState<T>(defaultValue)
  const [debouncedValue, setDebouncedState] = useState<T>(defaultValue)

  // debounce the second thing
  const debouncedSet = useMemo(
    () => debounce(setDebouncedState, delay),
    [delay],
  )

  // when value changes, set also debounced value
  useEffect(() => {
    debouncedSet(value)
  }, [value, debouncedSet])

  return [value, debouncedValue, setState] as const
}
