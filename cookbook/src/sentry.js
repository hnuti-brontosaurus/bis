import * as Sentry from "@sentry/vue"

const environment = import.meta.env.VITE_ENVIRONMENT

export function initSentry(app) {
  Sentry.init({
    app,
    dsn: "https://9d30aa568b4be2f4005228791c768051@o4504321204027392.ingest.us.sentry.io/4512372514226176",
    environment,
    enabled: ["dev", "prod"].includes(environment),
  })
}
