import { mock } from './support/api'
import { mockCurrentUser, ORGANIZER_ID } from './support/mocks'
import { expect, expectText, test } from './support/test'

const opportunityPath = `/api/frontend/users/${ORGANIZER_ID}/opportunities/1000/`

test.describe('update opportunity', () => {
  test.beforeEach(async ({ page }) => {
    await mockCurrentUser(page)
  })

  test.describe("opportunity doesn't exist", () => {
    test.beforeEach(async ({ page }) => {
      await mock(page, { pathname: opportunityPath }, { status: 404 })
    })

    test("should show 404 when opportunity doesn't exist", async ({ page }) => {
      await page.goto('/org/prilezitosti/1000/upravit')

      await expectText(page, '404')
      await expectText(page, 'Nepodařilo se nám najít příležitost')
    })
  })

  test.describe('opportunity exists', () => {
    test.beforeEach(async ({ page }) => {
      await mock(
        page,
        { method: 'GET', pathname: opportunityPath },
        { fixture: 'opportunity' },
      )
      await mock(
        page,
        { pathname: '/api/frontend/locations/100/' },
        { fixture: 'location' },
      )
      await mock(
        page,
        { method: 'GET', pathname: '/api/categories/opportunity_categories/' },
        { fixture: 'opportunityCategories' },
      )
    })

    test('should pre-fill the form with the data of the current opportunity', async ({
      page,
    }) => {
      await page.goto('/org/prilezitosti/1000/upravit')

      const category = page.locator(
        'input[type=radio][name=category]#location_help',
      )
      await expect(category).toBeHidden()
      await expect(category).toBeChecked()
      await expect(page.locator('input[name=name]')).toHaveValue('asdf')
      await expect(page.locator('[name=start]')).toHaveValue('2022-12-29')
      await expect(page.locator('[name=end]')).toHaveValue('2022-12-31')
    })

    test('should persist the data until canceled', async ({ page }) => {
      await page.goto('/org/prilezitosti/1000/upravit')

      await page.locator('input[name=name]').fill('somethingdifferent')
      // wait for redux-persist to flush to localStorage
      await expect
        .poll(() =>
          page.evaluate(() => window.localStorage.getItem('persist:form')),
        )
        .toContain('somethingdifferent')

      await page.reload()
      await expect(page.locator('input[name=name]')).toHaveValue(
        'somethingdifferent',
      )

      await page
        .locator('[type="reset"]', { hasText: 'Zrušit' })
        .first()
        .click()

      await page.goto('/org/prilezitosti/1000/upravit')
      await expect(page.locator('input[name=name]')).toHaveValue('asdf')
    })

    test('should send correct request(s) to backend when saving', async ({
      page,
    }) => {
      await page.goto('/org/prilezitosti/1000/upravit')

      await page.locator('input[name=name]').fill('New name')

      const updateOpportunity = await mock(
        page,
        { method: 'PATCH', pathname: opportunityPath },
        { fixture: 'opportunity' },
      )

      await page.locator('[type=submit]', { hasText: 'Uložit' }).first().click()

      expect((await updateOpportunity.first()).body).toMatchObject({
        name: 'New name',
        location: 100,
      })
    })
  })
})
