import type {
  FetchArgs,
  FetchBaseQueryError,
  FetchBaseQueryMeta,
} from '@reduxjs/toolkit/query'
import type {
  BaseQueryApi,
  QueryReturnValue,
} from '@reduxjs/toolkit/dist/query/baseQueryTypes'
import type { MaybePromise } from '@reduxjs/toolkit/dist/query/tsHelpers'
import type { PaginatedList } from './bisTypes'

const DEFAULT_PAGE_SIZE = 100

/**
 * Fetches every page of a paginated DRF endpoint in parallel.
 * Page 1 reveals `count`; pages 2..N are fired concurrently.
 * The browser caps concurrent connections per origin (~6), so the loop
 * stays bounded without an explicit limiter.
 *
 * Use as `queryFn:` on an RTK Query endpoint that needs every row.
 */
export const fetchAllPages =
  <TArg>(opts: {
    buildArgs: (params: {
      page: number
      pageSize: number
      arg: TArg
    }) => FetchArgs | string
    pageSize?: number
    maxItems?: (arg: TArg) => number | undefined
  }) =>
  async <TItem>(
    arg: TArg,
    _api: BaseQueryApi,
    _extraOptions: unknown,
    baseQuery: (
      args: FetchArgs | string,
    ) => MaybePromise<
      QueryReturnValue<unknown, FetchBaseQueryError, FetchBaseQueryMeta>
    >,
  ): Promise<
    QueryReturnValue<PaginatedList<TItem>, FetchBaseQueryError, object>
  > => {
    const pageSize = opts.pageSize ?? DEFAULT_PAGE_SIZE
    const maxItems = opts.maxItems?.(arg)

    const first = await baseQuery(opts.buildArgs({ page: 1, pageSize, arg }))
    if (first.error) return { error: first.error }
    const firstData = first.data as PaginatedList<TItem>

    if (!firstData.next) return { data: firstData }

    let totalPages = Math.ceil(firstData.count / pageSize)
    if (maxItems !== undefined) {
      totalPages = Math.min(totalPages, Math.ceil(maxItems / pageSize))
    }
    if (totalPages <= 1) return { data: firstData }

    const restPages = Array.from({ length: totalPages - 1 }, (_, i) => i + 2)
    const responses = await Promise.all(
      restPages.map(page => baseQuery(opts.buildArgs({ page, pageSize, arg }))),
    )

    const results: TItem[] = [...firstData.results]
    for (const response of responses) {
      if (response.error) return { error: response.error }
      results.push(...(response.data as PaginatedList<TItem>).results)
    }

    return {
      data: {
        count: firstData.count,
        next: null,
        previous: null,
        results: maxItems !== undefined ? results.slice(0, maxItems) : results,
      },
    }
  }
