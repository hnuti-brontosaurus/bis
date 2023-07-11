// https://docs.sentry.io/platforms/javascript/guides/react/components/errorboundary/#setting-a-fallback-function-render-props

import * as Sentry from '@sentry/react'
import { Button, Error } from 'components'

export const ErrorBoundaryFallback: Sentry.FallbackRender = ({
  error,
  componentStack,
  resetError,
}) => (
  <Error status={500} error={error}>
    <div>You have encountered an error</div>
    <div>{error.toString()}</div>
    <div>{componentStack}</div>
    <Button
      primary
      onClick={() => {
        /* When resetError() is called it will remove the Fallback component
        and render the Sentry ErrorBoundary's children in their initial state */
        resetError()
      }}
    >
      Click here to reset!
    </Button>
  </Error>
)
