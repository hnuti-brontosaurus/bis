import classNames from 'classnames'
import { Pagination } from 'components'
import { useSearchParamsState } from 'hooks/searchParamsState'
import { FC } from 'react'

/**
 * It's unscalable, because we have to provide all the data at the beginning
 * So when there are many items to list, we have to download them all at once
 *
 * We can provide additional props for table in this component
 */
export const UnscalablePaginatedList = <T, C extends {} = {}>({
  data,
  table,
  className,
  pageSize = 10,
  columnsToHideOnMobile,
  ...rest
}: {
  data: T[]
  table: FC<{ data: T[] } & C>
  className?: string
  pageSize?: number
  columnsToHideOnMobile?: number[]
} & C) => {
  const [page, setPage] = useSearchParamsState('s', 1, Number)
  const Table = table

  const tableData = data.slice((page - 1) * pageSize, page * pageSize)

  return (
    <div className={classNames(className)}>
      <Table
        data={tableData}
        {...(rest as unknown as C)}
        columnsToHideOnMobile={columnsToHideOnMobile}
      />
      <Pagination
        page={page}
        pages={Math.max(1, Math.ceil((data.length as number) / pageSize))}
        onPageChange={setPage}
      />
    </div>
  )
}
