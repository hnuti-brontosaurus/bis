// https://github.com/reduxjs/redux-toolkit/discussions/1171?sort=top#discussioncomment-2554980

/**
 * Usage: const results: result[] = useQueries(query: apiEndpoint, arguments: queryArument[])
 * query is api endpoint
 * arguments is array of arguments
 * results is array of results looking like array of useQuery() responses (each has isLoading, data, isSuccess, ...)
 */

import type { QueryActionCreatorResult } from '@reduxjs/toolkit/dist/query/core/buildInitiate'
import type { ApiEndpointQuery } from '@reduxjs/toolkit/dist/query/core/module'
import type {
  EndpointDefinitions,
  QueryDefinition,
} from '@reduxjs/toolkit/query'
import { store } from 'app/store'
import { useEffect } from 'react'
import { useSelector } from 'react-redux'

/**
 * Allows running a query on a collection of data
 * @param query The RTK ApiEndpointQuery to run
 * @param params a list of params that will be run by the query
 * @returns the rtk query result (same as useGetXQuery())
 */
export function useQueries<
  Q extends QueryDefinition<any, any, any, any>,
  D extends EndpointDefinitions,
>(
  query: ApiEndpointQuery<Q, D>,
  params: Parameters<typeof query['initiate']>[0][],
) {
  useEffect(() => {
    const results: QueryActionCreatorResult<any>[] = params.map(param =>
      store.dispatch(query.initiate(param as any)),
    )
    return () => {
      for (const result of results) {
        result.unsubscribe()
      }
    }
  }, [query, params])
  return useSelector(state =>
    params.map(param => query.select(param)(state as any)),
  )
}
