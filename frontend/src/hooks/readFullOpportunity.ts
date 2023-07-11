import { SerializedError } from '@reduxjs/toolkit'
import { FetchBaseQueryError, skipToken } from '@reduxjs/toolkit/query'
import { api } from 'app/services/bis'
import type { Location, Opportunity } from 'app/services/bisTypes'
import { Overwrite } from 'utility-types'

export type FullOpportunity = Overwrite<Opportunity, { location: Location }>

export const useReadFullOpportunity = (
  props:
    | {
        userId: string
        id: number
      }
    | typeof skipToken,
): {
  data: FullOpportunity | undefined
  isLoading: boolean
  isError: boolean
  isSuccess: boolean
  error: FetchBaseQueryError | SerializedError | undefined
} => {
  const opportunityQuery = api.endpoints.readOpportunity.useQuery(props)

  const opportunity = opportunityQuery.data
  const locationQuery = api.endpoints.readLocation.useQuery(
    opportunity?.location ? { id: opportunity.location } : skipToken,
  )

  const allQueries = [opportunityQuery, locationQuery]

  const isLoading = allQueries.some(query => query.isLoading)
  const isSuccess = allQueries.every(query => query.isSuccess)
  const isError = allQueries.some(query => query.isError)
  const error = allQueries.find(query => query.error)?.error

  return {
    data:
      opportunityQuery.data && locationQuery.data
        ? {
            ...opportunityQuery.data,
            location: locationQuery.data,
          }
        : undefined,
    isLoading,
    isSuccess,
    isError,
    error,
  }
}
