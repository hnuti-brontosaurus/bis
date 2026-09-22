import type { Page } from '@playwright/test'
import { mock } from './support/api'
import { anonymousTest as test, expect, expectText } from './support/test'

const answers = [
  { answer: 'answer first question', question: 4 },
  { answer: 'Option 1', question: 3 },
  { answer: 'Option 1, Option 3', question: 5 },
  { answer: 'answer to last question', question: 6 },
]

const fillQuestionnaire = async (page: Page) => {
  await page.locator('[name="answers.0.answer"]').fill('answer first question')
  await page.locator('[name="answers.1.answer"][value="Option 2"]').check()
  await page.locator('[name="answers.1.answer"][value="Option 1"]').check()

  await page.locator('[name="answers.2.answer"][value="Option 3"]').check()
  await page.locator('[name="answers.2.answer"][value="Option 1"]').check()
  await page
    .locator('[name="answers.3.answer"]')
    .fill('answer to last question')
}

test.describe('Standard event registration form', () => {
  test.describe('not signed in', () => {
    test.beforeEach(async ({ page }) => {
      await mock(
        page,
        { method: 'GET', pathname: '/api/web/events/2000/' },
        { fixture: 'webEvent' },
      )
    })

    test('should show form with personal data and questions', async ({
      page,
    }) => {
      await page.goto(
        '/akce/2000/prihlasit?next=https%3A%2F%2Fexample.com%2Fasdf%2Fghjkl',
      )

      await page.locator('[name=first_name]').fill('GivenName')
      await page.locator('[name=last_name]').fill('FamilyName')
      await page.locator('[name=birthday-day]').fill('12')
      await page.locator('[name=birthday-month]').fill('05')
      await page.locator('[name=birthday-year]').fill('1995')
      await page.locator('[name=phone]').fill('601001002')
      await page.locator('[name=email]').fill('test@example.com')
      await page.locator('[name=applicant_note]').fill('note')

      await fillQuestionnaire(page)

      const createApplication = await mock(page, {
        method: 'POST',
        pathname: '/api/frontend/events/2000/registration/applications/',
      })

      await page.locator('button', { hasText: 'Odeslat' }).first().click()

      expect((await createApplication.first()).body).toEqual({
        answers,
        close_person: null,
        first_name: 'GivenName',
        last_name: 'FamilyName',
        phone: '601001002',
        email: 'test@example.com',
        applicant_note: 'note',
        birthday: '1995-05-12',
        address: null,
        state: 'pending',
        is_child_application: false,
      })

      await expectText(page, 'Hotovo')
      await page.locator('button', { hasText: 'Hotovo' }).first().click()

      await expect(page).toHaveURL('https://example.com/asdf/ghjkl')
    })

    test('should fill and submit correct data for a child', async ({
      page,
    }) => {
      await page.goto(
        '/akce/2000/prihlasit?next=https%3A%2F%2Fexample.com%2Fasdf%2Fghjkl',
      )

      await page.locator('[name=is_child_application]').check()

      await page
        .locator('[name="close_person.first_name"]')
        .fill('ParentGivenName')
      await page
        .locator('[name="close_person.last_name"]')
        .fill('ParentFamilyName')
      await page.locator('[name="close_person.phone"]').fill('601001002')
      await page.locator('[name="close_person.email"]').fill('test@example.com')

      await page.locator('[name=first_name]').fill('GivenName')
      await page.locator('[name=last_name]').fill('FamilyName')
      await page.locator('[name=birthday-day]').fill('12')
      await page.locator('[name=birthday-month]').fill('05')
      await page.locator('[name=birthday-year]').fill('2015')
      await page.locator('[name=applicant_note]').fill('note')

      await fillQuestionnaire(page)

      const createApplication = await mock(page, {
        method: 'POST',
        pathname: '/api/frontend/events/2000/registration/applications/',
      })

      await page.locator('button', { hasText: 'Odeslat' }).first().click()

      expect((await createApplication.first()).body).toEqual({
        answers,
        close_person: {
          first_name: 'ParentGivenName',
          last_name: 'ParentFamilyName',
          phone: '601001002',
          email: 'test@example.com',
        },
        first_name: 'GivenName',
        last_name: 'FamilyName',
        phone: '',
        email: '',
        applicant_note: 'note',
        birthday: '2015-05-12',
        address: null,
        state: 'pending',
        is_child_application: true,
      })

      await expectText(page, 'Hotovo')
      await page.locator('button', { hasText: 'Hotovo' }).first().click()

      await expect(page).toHaveURL('https://example.com/asdf/ghjkl')
    })

    // Past event date checks (isEventPast) are unit tested in
    // src/utils/__tests__/helpers.test.ts
  })
})
