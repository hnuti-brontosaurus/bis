import './config'
import './index.scss'
// this line intentionally left blank
// it keeps reset stylesheets in index.scss, and generally the stuff above, imported first
import React from 'react'
import { createRoot } from 'react-dom/client'
import { Provider } from 'react-redux'
import { BrowserRouter } from 'react-router-dom'
import { PersistGate } from 'redux-persist/integration/react'
import { App } from './App'
import { persistor, store } from './app/store'
import { ErrorBoundary, ErrorBoundaryFallback } from './config/sentry'
import { SystemMessages } from './features/systemMessage/SystemMessages'
import { reportWebVitals } from './reportWebVitals'
import { redirectToOldBisOnAprilFools } from './utils/redirectToOldBis'

redirectToOldBisOnAprilFools()

// A tab opened before a deploy still asks for the previous build's chunks,
// which the new deploy no longer has. The URL has already changed by the time
// a lazy component loads, so a reload lands on the page that was asked for.
window.addEventListener('vite:preloadError', () => window.location.reload())

const container = document.getElementById('root')!
const root = createRoot(container)

root.render(
  <React.StrictMode>
    <ErrorBoundary fallback={ErrorBoundaryFallback}>
      <Provider store={store}>
        <PersistGate loading={null} persistor={persistor}>
          <BrowserRouter>
            <App />
            <SystemMessages />
          </BrowserRouter>
        </PersistGate>
      </Provider>
    </ErrorBoundary>
  </React.StrictMode>,
)

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals()
