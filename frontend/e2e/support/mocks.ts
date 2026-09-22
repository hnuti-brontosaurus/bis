import type { Page } from '@playwright/test'
import { mock, type Recorder, type Responder } from './api'
import { AUTH_TOKEN } from './test'

export const ORGANIZER_ID = '0419781d-06ba-432b-8617-797ea14cf848'

/**
 * Stubs the endpoints the app hits to resolve the signed-in user. The token
 * itself comes from seeded storage (see support/test.ts), so no spec has to
 * walk the login form unless that is what it is testing.
 */
export const mockCurrentUser = async (
  page: Page,
  user: Responder = { fixture: 'organizer' },
) => {
  await mock(
    page,
    { method: 'POST', pathname: '/api/auth/login/' },
    { body: { token: AUTH_TOKEN } },
  )
  await mock(
    page,
    { method: 'GET', pathname: '/api/auth/whoami/' },
    { body: { id: ORGANIZER_ID } },
  )
  await mock(
    page,
    { method: 'GET', pathname: `/api/frontend/users/${ORGANIZER_ID}/` },
    user,
  )
}

export const mockCategories = async (page: Page) => {
  const categories = {
    qualification_categories: 'qualificationCategories',
    health_insurance_companies: 'healthInsuranceCompanies',
    pronoun_categories: 'pronouns',
    event_categories: 'eventCategories',
    event_group_categories: 'eventGroupCategories',
    event_program_categories: 'eventProgramCategories',
    event_intended_for_categories: 'eventIntendedForCategories',
    diet_categories: 'dietCategories',
  }

  return Object.fromEntries(
    await Promise.all(
      Object.entries(categories).map(
        async ([endpoint, fixture]): Promise<[string, Recorder]> => [
          endpoint,
          await mock(
            page,
            { method: 'GET', pathname: `/api/categories/${endpoint}/` },
            { fixture },
          ),
        ],
      ),
    ),
  ) as Record<keyof typeof categories, Recorder>
}

export const mockFullEvent = async (
  page: Page,
  id = 1000,
  fixture = 'event',
) => {
  await mock(
    page,
    { method: 'GET', pathname: `/api/frontend/events/${id}/` },
    { fixture },
  )
  await mock(
    page,
    {
      method: 'GET',
      pathname: `/api/frontend/events/${id}/propagation/images/`,
    },
    { fixture: 'eventPropagationImages' },
  )
  await mock(
    page,
    {
      method: 'GET',
      pathname: `/api/frontend/events/${id}/registration/questionnaire/questions/`,
    },
    { body: { results: [] } },
  )
  await mock(
    page,
    {
      method: 'GET',
      pathname: `/api/frontend/events/${id}/feedback_form/inquiries/`,
    },
    { body: { results: [] } },
  )
  await mock(
    page,
    { method: 'GET', pathname: '/api/frontend/locations/100/' },
    { fixture: 'location' },
  )
  await mock(
    page,
    { method: 'GET', pathname: /\/api\/frontend\/users\/[a-z0-9-]+\/$/ },
    { fixture: 'organizer' },
  )
  await mock(
    page,
    { method: 'GET', pathname: '/api/frontend/users/' },
    { body: { results: [] } },
  )
}
