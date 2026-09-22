import type { Page } from '@playwright/test'
import type { User } from '../src/app/services/bisTypes'
import { mock } from './support/api'
import { ORGANIZER_ID } from './support/mocks'
import { anonymousTest as test, expectPath, expectText } from './support/test'

const organizer: User = {
  id: ORGANIZER_ID,
  roles: [
    {
      id: 1,
      name: 'asdf',
      slug: 'organizer',
    },
  ],
  qualifications: [
    {
      category: {
        id: 6,
        name: 'Vedoucí Brďo',
        slug: 'kids_leader',
        parents: [5],
      },
      valid_since: '01-01-2001',
      valid_till: '01-01-2400',
      approved_by: { first_name: 'fghj', last_name: 'hjkl' },
    },
  ],
  first_name: 'FirstName',
  last_name: 'LastName',
} as User

const user: User = Object.assign({}, organizer, { roles: [] })

const signIn = async (page: Page) => {
  await page.goto('/')
  await expectPath(page, '/login')

  await page.locator('input[name=email]').fill('asdf@example.com')
  await page.locator('input[name=password]').fill('correcthorsebatterystaples')
  await page.locator('[type=submit]').click()
}

test.describe('login', () => {
  test.beforeEach(async ({ page }) => {
    await mock(
      page,
      { method: 'POST', pathname: '/api/auth/login/' },
      { body: { token: '1234567890abcdef' } },
    )
    await mock(
      page,
      { method: 'GET', pathname: '/api/auth/whoami/' },
      { body: { id: ORGANIZER_ID } },
    )
  })

  test('can sign in as organizer', async ({ page }) => {
    await mock(
      page,
      { method: 'GET', pathname: '/api/frontend/users/*/' },
      { body: organizer },
    )

    await signIn(page)

    await expectPath(page, '/')
    await expectText(page, 'Po akci')
  })

  test('can sign in as user', async ({ page }) => {
    await mock(
      page,
      { method: 'GET', pathname: '/api/frontend/users/*/' },
      { body: user },
    )

    await signIn(page)

    await expectPath(page, '/')
    await expectText(page, 'Dárcovství')
  })
})
