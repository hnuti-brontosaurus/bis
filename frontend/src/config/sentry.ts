import * as Sentry from '@sentry/react'
import { BrowserTracing } from '@sentry/tracing'
import { useEffect } from 'react'
import {
  createRoutesFromChildren,
  matchRoutes,
  Routes as OriginalRoutes,
  useLocation,
  useNavigationType,
} from 'react-router-dom'

/*
set up using the following resources:
https://docs.sentry.io/platforms/javascript/guides/react/
https://docs.sentry.io/platforms/javascript/guides/react/components/errorboundary/
https://docs.sentry.io/platforms/javascript/guides/react/configuration/integrations/react-router/

to remove Sentry fully, remove this file and
replace ErrorBoundary with React.ErrorBoundary
figure out new fallback component
replace Routes with Routes from 'react-router-dom'
*/

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.VITE_ENVIRONMENT,
  integrations: [
    new BrowserTracing({
      routingInstrumentation: Sentry.reactRouterV6Instrumentation(
        useEffect,
        useLocation,
        useNavigationType,
        createRoutesFromChildren,
        matchRoutes,
      ),
    }),
  ],
  enabled:
    Boolean(import.meta.env.VITE_SENTRY_DSN) &&
    ['dev', 'prod'].includes(import.meta.env.VITE_ENVIRONMENT),
  // We recommend adjusting this value in production, or using tracesSampler
  // for finer control
  tracesSampleRate: 0,
  beforeSend: (event, { originalException }) => {
    // A submit handler's unwrap() rejects with RTK-Query's plain { status, data },
    // which Sentry would group into one issue for every failing request
    // in the app. One issue per page and status lets a new failure stand out.
    if (isApiError(originalException)) {
      const path = window.location.pathname.replace(
        /\/(\d+|[0-9a-f]{8}-[0-9a-f-]{27})(?=\/|$)/g,
        '/<id>',
      )
      const status = String(originalException.status)
      event.fingerprint = ['api-rejection', status, path]
      event.exception!.values![0].value = `API ${status} on ${path}`
    }
    return event
  },
})

const isApiError = (value: unknown): value is { status: unknown } =>
  typeof value === 'object' && value !== null && 'status' in value

export { ErrorBoundary } from '@sentry/react'
export { ErrorBoundaryFallback } from './ErrorBoundaryFallback'

export const Routes = Sentry.withSentryReactRouterV6Routing(OriginalRoutes)
