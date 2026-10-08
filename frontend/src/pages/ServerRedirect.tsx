import { useShowMessage } from 'features/systemMessage/useSystemMessage'
import { NotFound } from 'pages/NotFound'
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

/*
This component leaves the react app and goes to the same url
*/
export const ServerRedirect = ({
  notConfigured,
}: {
  notConfigured: string
}) => {
  const showMessage = useShowMessage()
  // The first location of a document has the key "default". Reaching this
  // route on it means the server handed the url to this app, so leaving for
  // the server again would loop.
  const servedByThisApp = useLocation().key === 'default'

  useEffect(() => {
    if (servedByThisApp) showMessage({ type: 'error', message: notConfigured })
    // eslint-disable-next-line no-self-assign
    else globalThis.location.href = globalThis.location.href
  }, [servedByThisApp, showMessage, notConfigured])

  return servedByThisApp ? <NotFound /> : null
}
