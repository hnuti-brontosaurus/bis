import * as Sentry from "@sentry/vue"

const environment = import.meta.env.VITE_ENVIRONMENT

export function initSentry(app) {
  Sentry.init({
    app,
    dsn: "https://4f39bc2515e0fa47a92343397485c035@o4504321204027392.ingest.us.sentry.io/4512372514291712",
    environment,
    enabled: ["dev", "prod"].includes(environment),
  })
}
