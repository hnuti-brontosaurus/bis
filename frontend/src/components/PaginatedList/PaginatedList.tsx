import classNames from 'classnames'
import { Pagination } from 'components'
import { FC } from 'react'

export const PAGE_SIZE = 10

export const PaginatedList = <T, C extends object = object>({
  data,
  totalCount,
  page,
  pageSize,
  onPageChange,
  table,
  className,
  columnsToHideOnMobile,
  ...rest
}: {
  data: T[]
  totalCount: number
  page: number
  pageSize: number
  onPageChange: (page: number) => void
  table: FC<{ data: T[] } & C>
  className?: string
  columnsToHideOnMobile?: number[]
} & C) => {
  const Table = table

  return (
    <div className={classNames(className)}>
      <Table
        data={data}
        {...(rest as unknown as C)}
        columnsToHideOnMobile={columnsToHideOnMobile}
      />
      <Pagination
        page={page}
        pages={Math.max(1, Math.ceil(totalCount / pageSize))}
        onPageChange={onPageChange}
      />
    </div>
  )
}
