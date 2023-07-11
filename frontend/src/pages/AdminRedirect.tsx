import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import { NotFound } from 'pages/NotFound'
import { useEffect } from 'react'

/*
This component leaves the react app and goes to the same url
*/
export const AdminRedirect = () => {
  const showMessage = useShowMessage()

  // inform user when admin access is not set up
  useEffect(() => {
    if (globalThis.document.referrer === globalThis.location.href)
      showMessage({
        type: 'error',
        message: 'Administrátorský přístup pro tuto doménu není nastavený',
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
