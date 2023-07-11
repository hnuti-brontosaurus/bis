// https://stackoverflow.com/a/34425083
// load script in react

import { useEffect } from 'react'

export const useScript = (url: string) => {
  useEffect(() => {
    const script = globalThis.document.createElement('script')

    script.src = url
    script.async = true

    globalThis.document.body.appendChild(script)

    return () => {
      globalThis.document.body.removeChild(script)
    }
  }, [url])
}
