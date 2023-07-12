/**
 * Convention for organizing api endpoints:
 *
 * Let's try to name endpoints starting
 * - `create` for `POST` requests
 * - `read` for `GET` requests
 *   - `readItem` to `GET` one item by id
 *   - `readItems` to `GET` list of items
 * - `update` for `PATCH` requests
 * - `delete` for `DELETE` requests
 *
 * e.g. `createEvent`, `readEvent`, `readEvents`, `updateEvent`, `deleteEvent`
 *
 * If you need to use `PUT` requests, try to figure other convention :)
 * Maybe `replace` or `put` or something... :)
 *
 * It's also very cool if you manage to group similar endpoints together
 *
 * TODO maybe we'll split this file into multiple
 */

// Need to use the React-specific entry point to import createApi
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { RootState } from 'app/store'
import { ClearBounds } from 'components'
import dayjs from 'dayjs'
import type { Assign, Overwrite } from 'utility-types'
import type {
  AdministrationUnit,
  AttendanceListPage,
  AttendanceListPagePayload,
  DietCategory,
  Event,
  EventApplication,
  EventApplicationPayload,
  EventCategory,
  EventGroupCategory,
  EventIntendedForCategory,
  EventPayload,
  EventPhoto,
  EventPhotoPayload,
  EventProgramCategory,
  EventPropagationImage,
  EventPropagationImagePayload,
  FinanceReceipt,
  HealthInsuranceCompany,
  Location,
  LoginRequest,
  MembershipCategory,
  Opportunity,
  OpportunityCategory,
  OpportunityPayload,
  PaginatedList,
  PatchedEventApplication,
  PronounCategory,
  QualificationCategory,
  Question,
  Questionnaire,
  Region,
  Registration,
  TokenResponse,
  User,
  UserPayload,
  UserSearch,
} from './bisTypes'

// Define a service using a base URL and expected endpoints
export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.REACT_APP_API_BASE_URL ?? '/api/',
    prepareHeaders: (headers, { getState }) => {
      // By default, if we have a token in the store, let's use that for authenticated requests
      const token = (getState() as RootState).auth.token
      if (token) {
        headers.set('authorization', `Token ${token}`)
      }
      return headers
    },
  }),
  tagTypes: [
    'Application',
    'AttendanceListPage',
    'User',
    'UserSearch',
    'Event',
    'WebEvent',
    'EventApplication',
    'EventImage',
    'EventPhoto',
    'EventQuestion',
    'FinanceReceipt',
    'Location',
    'Opportunity',
    'Participant',
  ],
  endpoints: build => ({
    /**
     * Authentication
     */
    login: build.mutation<TokenResponse, LoginRequest>({
      query: credentials => ({
        url: 'auth/login/',
        method: 'POST',
        body: credentials,
      }),
    }),
    logout: build.mutation<void, void>({
      query: () => ({ url: `auth/logout/`, method: 'POST' }),
    }),
    sendResetPasswordLink: build.mutation<unknown, { email: string }>({
      query: body => ({
        url: 'auth/send_verification_link/',
        method: 'POST',
        body,
      }),
    }),
    resetPassword: build.mutation<
      TokenResponse,
      { code: string; email: string; password: string }
    >({
      query: body => ({
        url: 'auth/reset_password/',
        method: 'POST',
        body,
      }),
    }),
    whoami: build.query<{ id: string }, void>({
      query: () => 'auth/whoami/',
    }),

    /**
     * Users
     */
    createUser: build.mutation<User, UserPayload>({
      query: queryArg => ({
        url: `frontend/users/`,
        method: 'POST',
        body: queryArg,
      }),
      invalidatesTags: () => [{ type: 'User' as const, id: 'USER_LIST' }],
    }),
    // frontendUsersRetrieve
    readUser: build.query<User, { id: string }>({
      query: ({ id }) => `frontend/users/${id}/`,
      providesTags: (result, error, { id }) => [{ type: 'User', id }],
    }),
    readUserByBirthdate: build.query<
      User,
      { first_name: string; last_name: string; birthday: string }
    >({
      query: queryArg => ({
        url: `frontend/get_unknown_user/`,
        params: {
          birthday: dayjs(queryArg.birthday, [
            'D-M-YYYY',
            'YYYY-MM-DD',
            'YYYY-M-D',
          ]).format('YYYY-MM-DD'),
          first_name: queryArg.first_name,
          last_name: queryArg.last_name,
        },
      }),
    }),
    readUsers: build.query<
      PaginatedList<User>,
      ListArguments & { id?: string[]; _search_id?: string[] }
    >({
      query: ({ id, _search_id, ...params }) => ({
        url: `frontend/users/`,
        params: {
          id: id?.join?.(','),
          _search_id: _search_id?.join?.(','),
          ...params,
        },
      }),
      providesTags: results =>
        results?.results
          ? results.results.map(user => ({
              type: 'User',
              id: user.id,
            }))
          : [],
    }),
    /**
     * Read (search) all users
     * This endpoint returns only very basic info about a user,
     * but searches the whole user database,
     * not just users visible to current user
     */
    readAllUsers: build.query<PaginatedList<UserSearch>, ListArguments>({
      query: queryArg => ({
        url: `frontend/search_users/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
      providesTags: results =>
        results?.results
          ? results.results.map(user => ({
              type: 'UserSearch',
              id: user._search_id,
            }))
          : [],
    }),
    updateUser: build.mutation<
      User,
      { patchedUser: Partial<UserPayload>; id: string }
    >({
      query: ({ id, patchedUser }) => ({
        url: `frontend/users/${id}/`,
        method: 'PATCH',
        body: patchedUser,
      }),
      invalidatesTags: (results, _, { id }) => [
        { type: 'User' as const, id: 'USER_LIST' },
        { type: 'User', id },
        { type: 'Participant', id: 'PARTICIPANT_LIST' },
      ],
    }),

    /**
     * Read various categories
     */
    readEventCategories: build.query<PaginatedList<EventCategory>, void>({
      query: () => ({
        url: `categories/event_categories/`,
      }),
    }),
    readEventGroups: build.query<PaginatedList<EventGroupCategory>, void>({
      query: () => ({
        url: `categories/event_group_categories/`,
      }),
    }),
    readPrograms: build.query<PaginatedList<EventProgramCategory>, void>({
      query: () => ({
        url: `categories/event_program_categories/`,
      }),
    }),
    readIntendedFor: build.query<PaginatedList<EventIntendedForCategory>, void>(
      {
        query: () => ({
          url: `categories/event_intended_for_categories/`,
        }),
      },
    ),
    readDiets: build.query<PaginatedList<DietCategory>, void>({
      query: () => ({
        url: `categories/diet_categories/`,
      }),
    }),
    readAdministrationUnits: build.query<
      PaginatedList<AdministrationUnit>,
      ListArguments & {
        /** Více hodnot lze oddělit čárkami. */
        category?: (
          | 'basic_section'
          | 'club'
          | 'headquarter'
          | 'regional_center'
        )[]
      }
    >({
      query: queryArg => ({
        url: `web/administration_units/`,
        params: {
          category: queryArg.category,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    readQualifications: build.query<
      PaginatedList<QualificationCategory>,
      ListArguments
    >({
      query: queryArg => ({
        url: `categories/qualification_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    readPronouns: build.query<PaginatedList<PronounCategory>, ListArguments>({
      query: queryArg => ({
        url: `categories/pronoun_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    readRegions: build.query<PaginatedList<Region>, ListArguments>({
      query: queryArg => ({
        url: `categories/regions/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    readHealthInsuranceCompanies: build.query<
      PaginatedList<HealthInsuranceCompany>,
      ListArguments
    >({
      query: queryArg => ({
        url: `categories/health_insurance_companies/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    readOpportunityCategories: build.query<
      PaginatedList<OpportunityCategory>,
      ListArguments
    >({
      query: queryArg => ({
        url: `categories/opportunity_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    readMembershipCategories: build.query<
      PaginatedList<MembershipCategory>,
      ListArguments
    >({
      query: queryArg => ({
        url: `categories/membership_categories/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),

    /**
     * Locations
     */
    createLocation: build.mutation<Location, Omit<Location, 'id'>>({
      query: queryArg => ({
        url: `frontend/locations/`,
        method: 'POST',
        body: queryArg,
      }),
      invalidatesTags: () => [
        { type: 'Location' as const, id: 'LOCATION_LIST' },
      ],
    }),
    readLocations: build.query<
      PaginatedList<Location>,
      {
        /** Více hodnot lze oddělit čárkami. */
        id?: number[]
        // This doesn't exist, but we want it!
        bounds?: ClearBounds
      } & ListArguments
    >({
      query: queryArg => ({
        url: `frontend/locations/`,
        params: {
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.bounds ? 5000 : queryArg.pageSize, // this will fetch everything (cry)
          search: queryArg.search,
        },
      }),
      providesTags: results =>
        (results?.results
          ? results.results.map(
              location =>
                ({
                  type: 'Location' as const,
                  id: location.id,
                } as { type: 'Location'; id: 'LOCATION_LIST' | number }),
            )
          : []
        ).concat([{ type: 'Location' as const, id: 'LOCATION_LIST' }]),
    }),
    readLocation: build.query<Location, { id: number }>({
      query: queryArg => ({ url: `frontend/locations/${queryArg.id}/` }),
      providesTags: (results, _, { id }) => [{ type: 'Location' as const, id }],
    }),
    updateLocation: build.mutation<
      Location,
      { id: number; location: Partial<Location> }
    >({
      query: queryArg => ({
        url: `frontend/locations/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.location,
      }),
      invalidatesTags: (results, _, { id }) => [
        { type: 'Location' as const, id: 'LOCATION_LIST' },
        { type: 'Location' as const, id },
      ],
    }),

    /**
     * Opportunities
     */
    readOpportunity: build.query<Opportunity, { userId: string; id: number }>({
      query: queryArg => ({
        url: `frontend/users/${queryArg.userId}/opportunities/${queryArg.id}/`,
      }),
      providesTags: (result, error, { id }) => [{ type: 'Opportunity', id }],
    }),
    readOpportunities: build.query<
      PaginatedList<Opportunity>,
      { userId: string; id?: number[] } & ListArguments
    >({
      query: queryArg => ({
        url: `frontend/users/${queryArg.userId}/opportunities/`,
        params: {
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
      providesTags: results =>
        (results?.results
          ? results.results.map(
              opportunity =>
                ({
                  type: 'Opportunity' as const,
                  id: opportunity.id,
                } as { type: 'Opportunity'; id: 'OPPORTUNITY_LIST' | number }),
            )
          : []
        ).concat([{ type: 'Opportunity' as const, id: 'OPPORTUNITY_LIST' }]),
    }),
    createOpportunity: build.mutation<
      Opportunity,
      { userId: string; opportunity: OpportunityPayload }
    >({
      query: ({ userId, opportunity }) => ({
        url: `frontend/users/${userId}/opportunities/`,
        method: 'POST',
        body: opportunity,
      }),
      invalidatesTags: () => [{ type: 'Opportunity', id: 'OPPORTUNITY_LIST' }],
    }),
    updateOpportunity: build.mutation<
      Opportunity,
      {
        id: number
        userId: string
        patchedOpportunity: Partial<OpportunityPayload>
      }
    >({
      query: queryArg => ({
        url: `frontend/users/${queryArg.userId}/opportunities/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedOpportunity,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Opportunity', id: 'OPPORTUNITY_LIST' },
        { type: 'Opportunity', id },
      ],
    }),
    deleteOpportunity: build.mutation<void, { id: number; userId: string }>({
      query: queryArg => ({
        url: `frontend/users/${queryArg.userId}/opportunities/${queryArg.id}/`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Opportunity', id: 'OPPORTUNITY_LIST' },
        { type: 'Opportunity', id },
      ],
    }),

    /**
     * Events
     */
    createEvent: build.mutation<Event, EventPayload>({
      query: event => ({
        url: `frontend/events/`,
        method: 'POST',
        body: event,
      }),
      invalidatesTags: () => [{ type: 'Event', id: 'ORGANIZED_EVENT_LIST' }],
    }),
    readEvent: build.query<Event, { id: number }>({
      query: queryArg => ({ url: `frontend/events/${queryArg.id}/` }),
      providesTags: (result, error, { id }) => [{ type: 'Event', id }],
    }),
    // Read only events currently shown on web
    // This endpoint provides data relevant to event display and registration
    readWebEvent: build.query<WebEvent, { id: number }>({
      query: queryArg => ({ url: `web/events/${queryArg.id}/` }),
      providesTags: (result, error, { id }) => [{ type: 'WebEvent', id }],
    }),
    readOrganizedEvents: build.query<
      PaginatedList<Event>,
      { userId: string; id?: number[] } & ListArguments
    >({
      query: queryArg => ({
        url: `frontend/users/${queryArg.userId}/events_where_was_organizer/`,
        params: {
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
      providesTags: results =>
        results?.results
          ? [
              ...results.results.map(event => ({
                type: 'Event' as const,
                id: event.id,
              })),
              {
                type: 'Event' as const,
                id: `ORGANIZED_EVENT_LIST`,
              },
            ]
          : [
              {
                type: 'Event' as const,
                id: `ORGANIZED_EVENT_LIST`,
              },
            ],
    }),
    updateEvent: build.mutation<
      Event,
      { id: number; event: Partial<EventPayload> }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.event,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Event', id },
        { type: 'Event', id: 'ORGANIZED_EVENT_LIST' },
        { type: 'Participant', id },
        { type: 'Participant', id: 'PARTICIPANT_LIST' },
      ],
    }),
    deleteEvent: build.mutation<void, { id: number }>({
      query: queryArg => ({
        url: `frontend/events/${queryArg.id}/`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Event', id },
        { type: 'Event', id: 'ORGANIZED_EVENT_LIST' },
      ],
    }),
    createEventImage: build.mutation<
      EventPropagationImage,
      { eventId: number; image: EventPropagationImagePayload }
    >({
      query: ({ eventId, image }) => ({
        url: `frontend/events/${eventId}/propagation/images/`,
        method: 'POST',
        body: image,
      }),
      invalidatesTags: (result, error, { eventId }) => [
        { type: 'EventImage', id: `${eventId}_IMAGE_LIST` },
      ],
    }),
    readEventImages: build.query<
      PaginatedList<EventPropagationImage>,
      { eventId: number } & ListArguments
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/propagation/images/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
      providesTags: (results, error, { eventId }) =>
        results?.results
          ? results.results
              .map(image => ({
                type: 'EventImage' as const,
                id: `${eventId}_${image.id}`,
              }))
              .concat([
                { type: 'EventImage' as const, id: `${eventId}_IMAGE_LIST` },
              ])
          : [],
    }),
    updateEventImage: build.mutation<
      EventPropagationImage,
      {
        eventId: number
        id: number
        image: Partial<EventPropagationImagePayload>
      }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/propagation/images/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.image,
      }),
      invalidatesTags: (result, error, { id, eventId }) => [
        { type: 'EventImage', id: `${eventId}_${id}` },
        { type: 'EventImage', id: `${eventId}_IMAGE_LIST` },
      ],
    }),
    deleteEventImage: build.mutation<void, { eventId: number; id: number }>({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/propagation/images/${queryArg.id}/`,
        method: 'DELETE',
      }),
      invalidatesTags: (_result, _error, { id, eventId }) => [
        { type: 'EventImage', id: `${eventId}_${id}` },
        { type: 'EventImage', id: `${eventId}_IMAGE_LIST` },
      ],
    }),
    createEventQuestion: build.mutation<
      Question,
      { eventId: number; question: Omit<Question, 'id'> }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/registration/questionnaire/questions/`,
        method: 'POST',
        body: queryArg.question,
      }),
      invalidatesTags: (_result, _error, { eventId }) => [
        { type: 'EventQuestion', id: `${eventId}_QUESTION_LIST` },
        { type: 'WebEvent', id: eventId },
      ],
    }),
    readEventQuestions: build.query<
      PaginatedList<Question>,
      { eventId: number } & ListArguments
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/registration/questionnaire/questions/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
      providesTags: (results, error, { eventId }) =>
        results?.results
          ? results.results
              .map(question => ({
                type: 'EventQuestion' as const,
                id: `${eventId}_${question.id}`,
              }))
              .concat([
                {
                  type: 'EventQuestion' as const,
                  id: `${eventId}_QUESTION_LIST`,
                },
              ])
          : [],
    }),
    updateEventQuestion: build.mutation<
      Question,
      { eventId: number; id: number; question: Partial<Omit<Question, 'id'>> }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/registration/questionnaire/questions/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.question,
      }),
      invalidatesTags: (_result, _error, { id, eventId }) => [
        { type: 'EventQuestion', id: `${eventId}_${id}` },
        { type: 'EventQuestion', id: `${eventId}_QUESTION_LIST` },
        { type: 'WebEvent', id: eventId },
      ],
    }),
    deleteEventQuestion: build.mutation<void, { eventId: number; id: number }>({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/registration/questionnaire/questions/${queryArg.id}/`,
        method: 'DELETE',
      }),
      invalidatesTags: (_result, _error, { id, eventId }) => [
        { type: 'EventQuestion', id: `${eventId}_${id}` },
        { type: 'EventQuestion', id: `${eventId}_QUESTION_LIST` },
        { type: 'WebEvent', id: eventId },
      ],
    }),
    createFinanceReceipt: build.mutation<
      FinanceReceipt,
      {
        eventId: number
        financeReceipt: Omit<FinanceReceipt, 'id'>
      }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/finance/receipts/`,
        method: 'POST',
        body: queryArg.financeReceipt,
      }),
      invalidatesTags: (result, error, { eventId }) => [
        { type: 'FinanceReceipt', id: `${eventId}_RECEIPT_LIST` },
      ],
    }),
    readFinanceReceipts: build.query<
      PaginatedList<FinanceReceipt>,
      ListArguments & { eventId: number }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/finance/receipts/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
      providesTags: (results, error, { eventId }) =>
        results?.results
          ? results.results
              .map(receipt => ({
                type: 'FinanceReceipt' as const,
                id: `${eventId}_${receipt.id}`,
              }))
              .concat([
                {
                  type: 'FinanceReceipt' as const,
                  id: `${eventId}_RECEIPT_LIST`,
                },
              ])
          : [],
    }),
    updateFinanceReceipt: build.mutation<
      FinanceReceipt,
      {
        eventId: number
        id: number
        patchedFinanceReceipt: Partial<FinanceReceipt>
      }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/finance/receipts/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedFinanceReceipt,
      }),
      invalidatesTags: (result, error, { id, eventId }) => [
        { type: 'FinanceReceipt', id: `${eventId}_${id}` },
        { type: 'FinanceReceipt', id: `${eventId}_RECEIPT_LIST` },
      ],
    }),
    deleteFinanceReceipt: build.mutation<void, { eventId: number; id: number }>(
      {
        query: queryArg => ({
          url: `frontend/events/${queryArg.eventId}/finance/receipts/${queryArg.id}/`,
          method: 'DELETE',
        }),
        invalidatesTags: (result, error, { id, eventId }) => [
          { type: 'FinanceReceipt', id: `${eventId}_${id}` },
          { type: 'FinanceReceipt', id: `${eventId}_RECEIPT_LIST` },
        ],
      },
    ),
    createEventApplication: build.mutation<
      EventApplication,
      { application: EventApplicationPayload; eventId: number }
    >({
      query: ({ application, eventId }) => ({
        url: `frontend/events/${eventId}/registration/applications/`,
        method: 'POST',
        body: application,
      }),
      invalidatesTags: () => [{ type: 'Application', id: 'APPLICATION_LIST' }],
    }),
    readEventApplication: build.query<
      EventApplication,
      { applicationId: number; eventId: number }
    >({
      query: ({ applicationId, eventId }) => ({
        url: `frontend/events/${eventId}/registration/applications/${applicationId}/`,
        method: 'GET',
      }),
    }),
    readEventApplications: build.query<
      PaginatedList<EventApplication>,
      { eventId: number; id?: number[] | undefined } & ListArguments
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/registration/applications/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
      providesTags: results =>
        (results?.results
          ? results.results.map(
              application =>
                ({
                  type: 'Application' as const,
                  id: application.id,
                } as { type: 'Application'; id: 'APPLICATION_LIST' | number }),
            )
          : []
        ).concat([{ type: 'Application' as const, id: 'APPLICATION_LIST' }]),
    }),
    updateEventApplication: build.mutation<
      EventApplication,
      {
        eventId: number
        /** A unique integer value identifying this Přihláška na akci. */
        id: number
        patchedEventApplication: PatchedEventApplication
      }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/registration/applications/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedEventApplication,
      }),
      invalidatesTags: () => [{ type: 'Application', id: 'APPLICATION_LIST' }],
    }),
    deleteEventApplication: build.mutation<
      void,
      { applicationId: number; eventId: number }
    >({
      query: ({ applicationId, eventId }) => ({
        url: `frontend/events/${eventId}/registration/applications/${applicationId}/`,
        method: 'DELETE',
      }),
      invalidatesTags: () => [{ type: 'Application', id: 'APPLICATION_LIST' }],
    }),
    readEventParticipants: build.query<
      PaginatedList<User>,
      { eventId: number } & ListArguments
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/record/participants/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
      providesTags: results =>
        (results?.results
          ? results.results.map(
              participant =>
                ({
                  type: 'Participant' as const,
                  id: participant.id,
                } as { type: 'Participant'; id: 'PARTICIPANT_LIST' | number }),
            )
          : []
        ).concat([{ type: 'Participant' as const, id: 'PARTICIPANT_LIST' }]),
    }),
    // /**
    //  * Please don't use this endpoint!
    //  * It'll fill cache with blob, and that can potentially crash our application
    //  * use the useExportAttendanceList hook
    //  */
    // exportEventAttendanceList: build.query<
    //   Blob,
    //   { eventId: number; formatting?: 'pdf' | 'xlsx' }
    // >({
    //   query: queryArg => ({
    //     url: `frontend/events/${queryArg.eventId}/get_attendance_list/`,
    //     params: { formatting: queryArg.formatting },
    //     responseType: 'blob',
    //   }),
    // }),
    readAttendanceListPages: build.query<
      PaginatedList<AttendanceListPage>,
      ListArguments & { eventId: number }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/record/attendance_list_pages/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
      providesTags: (results, error, { eventId }) =>
        results?.results
          ? results.results
              .map(receipt => ({
                type: 'AttendanceListPage' as const,
                id: `${eventId}_${receipt.id}`,
              }))
              .concat([
                {
                  type: 'AttendanceListPage' as const,
                  id: `${eventId}_ATTENDANCE_LIST`,
                },
              ])
          : [],
    }),
    createAttendanceListPage: build.mutation<
      AttendanceListPage,
      { eventId: number; eventAttendanceListPage: AttendanceListPagePayload }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/record/attendance_list_pages/`,
        method: 'POST',
        body: queryArg.eventAttendanceListPage,
      }),
      invalidatesTags: (result, error, { eventId }) => [
        { type: 'AttendanceListPage', id: `${eventId}_ATTENDANCE_LIST` },
      ],
    }),
    updateAttendanceListPage: build.mutation<
      AttendanceListPage,
      {
        eventId: number
        id: number
        patchedAttendanceListPage: Partial<AttendanceListPagePayload>
      }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/record/attendance_list_pages/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedAttendanceListPage,
      }),
      invalidatesTags: (result, error, { id, eventId }) => [
        { type: 'AttendanceListPage', id: `${eventId}_${id}` },
        { type: 'AttendanceListPage', id: `${eventId}_ATTENDANCE_LIST` },
      ],
    }),
    deleteAttendanceListPage: build.mutation<
      void,
      { eventId: number; id: number }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/record/attendance_list_pages/${queryArg.id}/`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, { id, eventId }) => [
        { type: 'AttendanceListPage', id: `${eventId}_${id}` },
        { type: 'AttendanceListPage', id: `${eventId}_ATTENDANCE_LIST` },
      ],
    }),
    createEventPhoto: build.mutation<
      EventPhoto,
      { eventId: number; eventPhoto: EventPhotoPayload }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/record/photos/`,
        method: 'POST',
        body: queryArg.eventPhoto,
      }),
      invalidatesTags: (result, error, { eventId }) => [
        { type: 'EventPhoto', id: `${eventId}_EVENT_PHOTO_LIST` },
      ],
    }),
    readEventPhotos: build.query<
      PaginatedList<EventPhoto>,
      ListArguments & { eventId: number }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/record/photos/`,
        params: {
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
      providesTags: (results, error, { eventId }) =>
        results?.results
          ? results.results
              .map(receipt => ({
                type: 'EventPhoto' as const,
                id: `${eventId}_${receipt.id}`,
              }))
              .concat([
                {
                  type: 'EventPhoto' as const,
                  id: `${eventId}_EVENT_PHOTO_LIST`,
                },
              ])
          : [],
    }),
    updateEventPhoto: build.mutation<
      EventPhoto,
      {
        eventId: number
        id: number
        patchedEventPhoto: Partial<EventPhotoPayload>
      }
    >({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/record/photos/${queryArg.id}/`,
        method: 'PATCH',
        body: queryArg.patchedEventPhoto,
      }),
      invalidatesTags: (result, error, { id, eventId }) => [
        { type: 'EventPhoto', id: `${eventId}_${id}` },
        { type: 'EventPhoto', id: `${eventId}_EVENT_PHOTO_LIST` },
      ],
    }),
    deleteEventPhoto: build.mutation<void, { eventId: number; id: number }>({
      query: queryArg => ({
        url: `frontend/events/${queryArg.eventId}/record/photos/${queryArg.id}/`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, { id, eventId }) => [
        { type: 'EventPhoto', id: `${eventId}_${id}` },
        { type: 'EventPhoto', id: `${eventId}_EVENT_PHOTO_LIST` },
      ],
    }),
    /**
     * Event endpoints for user (the others are mostly for org)
     */
    readParticipatedEvents: build.query<
      PaginatedList<Event>,
      { id?: number[]; userId: string } & ListArguments
    >({
      query: queryArg => ({
        url: `frontend/users/${queryArg.userId}/participated_in_events/`,
        params: {
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),
    readRegisteredEvents: build.query<
      PaginatedList<Event>,
      { id?: number[]; userId: string } & ListArguments
    >({
      query: queryArg => ({
        url: `frontend/users/${queryArg.userId}/registered_in_events/`,
        params: {
          id: queryArg.id,
          page: queryArg.page,
          page_size: queryArg.pageSize,
          search: queryArg.search,
        },
      }),
    }),

    // this endpoints searches GPS by search string
    // using https://nominatim.openstreetmap.org
    // before using it, please refer to it's usage policy
    // https://operations.osmfoundation.org/policies/nominatim/
    // e.g. it's forbidden to do autocomplete queries with it (i.e. search as you type)
    // and the whole application needs to send less than 1 request per second, as absolute maximum
    searchLocationOSM: build.query<OSMLocation[], string>({
      query: arg => ({
        url: `https://nominatim.openstreetmap.org/search.php?q=${encodeURIComponent(
          arg,
        )}&accept-language=cs&format=jsonv2`,
      }),
      transformResponse: (a: RawOSMLocation[]) =>
        a.map(
          ({ lat, lon, boundingbox: [lat1, lat2, lon1, lon2], ...rest }) => ({
            lat: Number(lat),
            lon: Number(lon),
            boundingbox: [
              [Number(lat1), Number(lon1)],
              [Number(lat2), Number(lon2)],
            ], // as [[number, number], [number, number]],
            ...rest,
          }),
        ),
    }),
  }),
})

export type RawOSMLocation = {
  lat: string
  lon: string
  boundingbox: [string, string, string, string]
  display_name: string
}

export type OSMLocation = Overwrite<
  RawOSMLocation,
  {
    lat: number
    lon: number
    boundingbox: [[number, number], [number, number]]
  }
>

interface ListArguments {
  /** A page number within the paginated result set. */
  page?: number
  /** Number of results to return per page. */
  pageSize?: number
  /** A search term. */
  search?: string
}

export type WebQuestionnaire = Assign<Questionnaire, { questions: Question[] }>
type WebRegistration = Overwrite<
  Registration,
  { questionnaire: WebQuestionnaire | null }
>

export type WebEvent = Overwrite<
  Event,
  {
    registration: WebRegistration | null
    location?: Location
  }
>
