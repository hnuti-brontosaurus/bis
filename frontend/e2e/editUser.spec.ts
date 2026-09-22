import { mock } from './support/api'
import { mockCategories, mockCurrentUser } from './support/mocks'
import { expect, test } from './support/test'

test.describe('Edit user', () => {
  test.beforeEach(async ({ page }) => {
    await mockCategories(page)
    await mockCurrentUser(page)
  })

  test.describe('myself', () => {
    test('should be able to save my preferred pronoun', async ({ page }) => {
      await mock(
        page,
        { method: 'GET', pathname: '/api/frontend/users/1234/' },
        { fixture: 'organizer' },
      )
      await page.goto('/profil/1234/upravit')

      await expect(page.locator('form')).toContainText('Oslovení')
      const pronoun = page.locator('[name=pronoun]')
      await expect(pronoun).toHaveValue('1')
      await pronoun.selectOption('2')

      const updateUser = await mock(page, {
        method: 'PATCH',
        pathname: '/api/frontend/users/*/',
      })
      await page.locator('button', { hasText: 'Potvrdit' }).first().click()

      expect((await updateUser.first()).body).toHaveProperty('pronoun', 2)
    })

    test('should be able to save no pronoun', async ({ page }) => {
      await mock(
        page,
        { method: 'GET', pathname: '/api/frontend/users/1234/' },
        { fixture: 'organizer' },
      )
      await page.goto('/profil/1234/upravit')

      await expect(page.locator('form')).toContainText('Oslovení')
      const pronoun = page.locator('[name=pronoun]')
      await expect(pronoun).toHaveValue('1')
      await pronoun.selectOption({ index: 0 })

      const updateUser = await mock(page, {
        method: 'PATCH',
        pathname: '/api/frontend/users/*/',
      })
      await mock(
        page,
        { method: 'GET', pathname: '/api/frontend/users/*/' },
        { fixture: 'organizer' },
      )
      await page.locator('button', { hasText: 'Potvrdit' }).first().click()

      expect((await updateUser.first()).body).toHaveProperty('pronoun', null)
    })
  })

  test.describe('other user', () => {
    test('[i have access] should not be able to save pronoun', async ({
      page,
    }) => {
      await mock(
        page,
        { method: 'GET', pathname: '/api/frontend/users/1234/' },
        { fixture: 'chairman' },
      )
      await page.goto('/profil/1234/upravit')

      await expect(page.locator('form')).not.toContainText('Oslovení')
      await expect(page.locator('[name=pronoun]')).toHaveCount(0)

      const updateUser = await mock(page, {
        method: 'PATCH',
        pathname: '/api/frontend/users/*/',
      })
      await page.locator('button', { hasText: 'Potvrdit' }).first().click()

      expect((await updateUser.first()).body).not.toHaveProperty('pronoun')
    })

    test.fixme("[i don't have access] should show 403 error", () => {
      // Deliberately unimplemented; kept so the gap shows up in the report.
    })
  })
})
