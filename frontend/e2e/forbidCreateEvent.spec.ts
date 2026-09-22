import { mock } from './support/api'
import { mockCategories, mockCurrentUser } from './support/mocks'
import { expect, expectPath, expectText, test } from './support/test'

/**
 * Skipped on purpose: right now every organizer may create events. Drop the
 * `.skip` to re-enable the rule that organizers without qualifications cannot.
 */
test.describe.skip('create event', () => {
  test.beforeEach(async ({ page }) => {
    await mockCategories(page)
    await mockCurrentUser(page, { fixture: 'organizerWithoutQualifications' })
    await mock(
      page,
      { method: 'GET', pathname: /\/api\/frontend\/users\/[a-zA-Z0-9-]+\/$/ },
      { fixture: 'organizerWithoutQualifications' },
    )
  })

  test('shows a gray "NOVA AKCE" button that is disabled', async ({ page }) => {
    await page.goto('/org/')
    await expectPath(page, '/org/')

    const createEvent = page.locator('a[id=createEvent]')
    await expect(createEvent).toHaveCSS(
      'background-color',
      'rgb(244, 248, 250)',
    )
    await expect(createEvent).toHaveCSS('pointer-events', 'none')
  })

  test("can't fill form and send data to create a new event", async ({
    page,
  }) => {
    await page.goto('/org/akce/vytvorit')
    await expectPath(page, '/org/akce/vytvorit')

    await expectText(
      page,
      'Nemáš dostatečná práva k TODO text organizátorskému přístupu',
    )
  })

  test("can't clone an event", async ({ page }) => {
    await page.goto('/org/akce/vytvorit?klonovat=1000')

    await expectText(
      page,
      'Nemáš dostatečná práva k TODO text organizátorskému přístupu',
    )
  })
})
