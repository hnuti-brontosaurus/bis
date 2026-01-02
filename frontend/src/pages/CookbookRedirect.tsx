import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import { NotFound } from 'pages/NotFound'
import { useEffect } from 'react'

/*
This component leaves the react app and goes to the same url
*/
export const CookbookRedirect = () => {
  const showMessage = useShowMessage()

  // inform user when admin access is not set up
  useEffect(() => {
    if (globalThis.document.referrer === globalThis.location.href)
      showMessage({
        type: 'error',
        message: 'Kuchařka není pro tuto doménu nastavená',
      })
  }, [showMessage])

  // prevent infinite redirect loop
  if (globalThis.document.referrer === globalThis.location.href) {
    return <NotFound />
  }

  // eslint-disable-next-line no-self-assign
  globalThis.location.href = globalThis.location.href

  return null
}
