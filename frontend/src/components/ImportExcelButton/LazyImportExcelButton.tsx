import { lazy, Suspense } from 'react'
import type { ImportExcelButtonProps } from './ImportExcelButton'

const ImportExcelButton = lazy(() => import('./ImportExcelButton')) as <
  T extends Record<string, unknown>,
>(
  props: ImportExcelButtonProps<T>,
) => JSX.Element

export const LazyImportExcelButton = <T extends Record<string, unknown>>(
  props: ImportExcelButtonProps<T>,
) => (
  <Suspense>
    <ImportExcelButton<T> {...props} />
  </Suspense>
)
