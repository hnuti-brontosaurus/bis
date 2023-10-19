import { useEffect } from 'react'

export const useKeyDown = (callback: () => void, keys: string[]) => {
  const onKeyDown = (event: KeyboardEvent) => {
    const wasAnyKeyDowned = keys.some((key: string) => event.key === key)
    if (wasAnyKeyDowned) {
      event.preventDefault()
      callback()
    }
  }
  useEffect(() => {
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [onKeyDown])
}
