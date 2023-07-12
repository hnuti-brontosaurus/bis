import { lazy, Suspense } from 'react'
import type { ImportExcelButtonProps } from './ImportExcelButton'

const ImportExcelButton = lazy(() => import('./ImportExcelButton')) as <
  T extends {},
>(
  props: ImportExcelButtonProps<T>,
) => JSX.Element

export const LazyImportExcelButton = <T extends {}>(
  props: ImportExcelButtonProps<T>,
) => (
  <Suspense>
    <ImportExcelButton<T> {...props} />
  </Suspense>
)
