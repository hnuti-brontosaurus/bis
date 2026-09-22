/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_E2E: string
  readonly VITE_ENVIRONMENT: 'local' | 'testing' | 'dev' | 'prod'
  readonly VITE_SENTRY_DSN: string
  readonly VITE_MAPY_CZ_API_KEY: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
