import type { Page } from '@playwright/test'
import { mock } from './support/api'
import { mockCurrentUser } from './support/mocks'
import { expect, expectPath, PERSISTED_AUTH_KEY, test } from './support/test'

const readPersistedAuth = (page: Page) =>
  page.evaluate(key => window.localStorage.getItem(key), PERSISTED_AUTH_KEY)

test.describe('Sign out', () => {
  test.beforeEach(async ({ page }) => {
    await mockCurrentUser(page)
    await page.goto('/')
    await expectPath(page, '/')
  })

  test('should sign out when going to /logout', async ({ page }) => {
    expect(await readPersistedAuth(page)).not.toBeNull()

    await mock(page, { pathname: '/api/auth/logout/' })
    await page.goto('/logout')

    await expectPath(page, '/login')
    await expect.poll(() => readPersistedAuth(page)).toBeNull()
  })

  test('should sign out when going to /logout even when api fails', async ({
    page,
  }) => {
    expect(await readPersistedAuth(page)).not.toBeNull()

    await mock(page, { pathname: '/api/auth/logout/' }, { status: 500 })
    await page.goto('/logout')

    await expectPath(page, '/login')
    await expect.poll(() => readPersistedAuth(page)).toBeNull()
  })
})
