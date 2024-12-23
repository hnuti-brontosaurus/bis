import { SerializedError } from '@reduxjs/toolkit'
import { FetchBaseQueryError, skipToken } from '@reduxjs/toolkit/query'
import { ALL_USERS, api } from 'app/services/bis'
import type { FullEvent } from 'app/services/bisTypes'
import { User } from 'app/services/bisTypes'

export const useReadFullEvent = (
  eventId: number,
): {
  data: FullEvent | undefined
  isLoading: boolean
  isError: boolean
  isSuccess: boolean
  error: FetchBaseQueryError | SerializedError | undefined
} => {
  const eventQuery = api.endpoints.readEvent.useQuery(
    eventId > 0 ? { id: eventId } : skipToken,
  )
  const event = eventQuery.data
  const imagesQuery = api.endpoints.readEventImages.useQuery(
    eventId > 0 ? { eventId } : skipToken,
  )
  const questionsQuery = api.endpoints.readEventQuestions.useQuery(
    eventId > 0
      ? {
          eventId,
        }
      : skipToken,
  )
  const mainOrganizerQuery = api.endpoints.readUser.useQuery(
    event?.main_organizer ? { id: event.main_organizer } : skipToken,
  )
  const otherOrganizersQuery = api.endpoints.readUsers.useQuery(
    // @ts-ignore
    event?.other_organizers
      ? { id: event.other_organizers, pageSize: ALL_USERS }
      : skipToken,
  )
  const locationQuery = api.endpoints.readLocation.useQuery(
    event?.location ? { id: event.location } : skipToken,
  )

  const allQueries = [
    eventQuery,
    imagesQuery,
    questionsQuery,
    mainOrganizerQuery,
    otherOrganizersQuery,
    locationQuery,
  ]

  const isLoading = allQueries.some(query => query.isLoading)
  const isSuccess = allQueries.every(query => query.isSuccess)
  const isError = allQueries.some(query => query.isError)
  const error = allQueries.find(query => query.error)?.error

  return {
    data:
      eventQuery.data &&
      imagesQuery.data &&
      (!eventQuery.data.main_organizer || mainOrganizerQuery.data) &&
      otherOrganizersQuery.data &&
      questionsQuery.data &&
      (!eventQuery.data.location || locationQuery.data)
        ? {
            ...eventQuery.data,
            main_organizer: mainOrganizerQuery.data as User, // in some old events this might be missing
            other_organizers: otherOrganizersQuery.data.results,
            images: imagesQuery.data.results,
            questions: questionsQuery.data.results,
            location:
              (eventQuery.data.location && locationQuery.data) || undefined,
          }
        : undefined,
    isLoading,
    isSuccess,
    isError,
    error,
  }
}
