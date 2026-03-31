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
    import.meta.env.MODE !== 'development',
  // We recommend adjusting this value in production, or using tracesSampler
  // for finer control
  tracesSampleRate: 0,
})

export { ErrorBoundary } from '@sentry/react'
export { ErrorBoundaryFallback } from './ErrorBoundaryFallback'

export const Routes = Sentry.withSentryReactRouterV6Routing(OriginalRoutes)
