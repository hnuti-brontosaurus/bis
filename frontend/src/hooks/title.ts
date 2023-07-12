import { useEffect } from 'react'

// https://stackoverflow.com/a/64352116
// set title of a page
export const useTitle = (title: string) => {
  useEffect(() => {
    const prevTitle = document.title
    document.title = `${title} \u2014 BIS`
    return () => {
      document.title = prevTitle
    }
  }, [title])
}
