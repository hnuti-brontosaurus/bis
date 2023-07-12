// polyfills must be imported first
// https://github.com/facebook/create-react-app/blob/main/packages/react-app-polyfill/README.md#polyfilling-other-language-features
import 'react-app-polyfill/ie11'
import 'react-app-polyfill/stable'
// this line intentionally left blank
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
