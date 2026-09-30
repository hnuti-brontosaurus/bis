import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import { NotFound } from 'pages/NotFound'
import { useEffect } from 'react'

/*
This component leaves the react app and goes to the same url
*/
export const ServerRedirect = ({
  notConfigured,
}: {
  notConfigured: string
}) => {
  const showMessage = useShowMessage()

  // the server sent us back here, so nothing but this app serves the url
  useEffect(() => {
    if (globalThis.document.referrer === globalThis.location.href)
      showMessage({ type: 'error', message: notConfigured })
  }, [showMessage, notConfigured])

  // prevent infinite redirect loop
  if (globalThis.document.referrer === globalThis.location.href) {
    return <NotFound />
  }

  // eslint-disable-next-line no-self-assign
  globalThis.location.href = globalThis.location.href

  return null
}
