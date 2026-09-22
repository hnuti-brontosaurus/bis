import type { Page } from '@playwright/test'
import type { Location } from '../src/app/services/bisTypes'
import { asset, fixture, mock } from './support/api'
import { mockCategories, mockCurrentUser, mockFullEvent } from './support/mocks'
import { expect, expectPath, expectText, test } from './support/test'

const searchUsers = new Array(47).fill('').map((val, i) => ({
  _search_id: String(i),
  first_name: `FirstName${i}`,
  last_name: `LastName${i}`,
  nickname: `Nickname${i}`,
  display_name: `Displayname${i}`,
}))

const locations: Location[] = new Array(35)
  .fill('')
  .map((val, i) => ({
    id: i,
    name: `Location ${i}`,
    gps_location: {
      type: 'Point',
      coordinates: [12 + Math.random() * 7, 49 + Math.random() * 2],
    },
  }))
  .flat() as Location[]

const next = (page: Page) =>
  page.locator('button[aria-label="Go to next step"]').first().click()

const submit = (page: Page) =>
  page.locator('[type=submit]', { hasText: 'Uložit' }).last().click()

const pickFromReactSelect = async (
  page: Page,
  id: number,
  keys: string[],
  search?: string,
  { force = false } = {},
) => {
  const input = page.locator(`#react-select-${id}-input`)
  await input.click({ force })
  if (search !== undefined) {
    await input.pressSequentially(search)
    await expect(
      page.locator(`[id^=react-select-${id}-option]`).first(),
    ).toBeAttached()
  }
  for (const key of keys) await input.press(key)
}

/**
 * Re-selecting the same file leaves the input's FileList unchanged, so the
 * second add would never fire `change`. Clearing it first makes each add real.
 */
const addImage = async (page: Page) => {
  const input = page.locator('[name="images.add"]')
  await input.setInputFiles([])
  await input.setInputFiles(asset('image.png'))
}

/** Quill renders a contenteditable div, so the id is on the wrapper, not an input. */
const fillRichText = (page: Page, name: string, text: string) =>
  page.locator(`[id="${name}"] .ql-editor`).fill(text)

const mockUnknownUser = (page: Page, memberships: { year: number }[]) =>
  mock(
    page,
    { method: 'GET', pathname: '/api/frontend/get_unknown_user/' },
    {
      body: {
        id: '1345',
        first_name: 'FirstName',
        last_name: 'LastName',
        nickname: 'Nickname',
        _search_id: '27',
        display_name: 'Found User',
        birthday: '2000-01-01',
        qualifications: [],
        memberships,
      },
    },
  )

/** Opens the create-event page, pre-fills the fields and moves to the "team" tab. */
const fillForm = async (page: Page) => {
  await page.goto('/org/akce/vytvorit')
  await expectPath(page, '/org/akce/vytvorit')

  await page.locator('label[for=other]').click()
  await next(page)

  await page.locator('input[name=name]').fill('Event Name III')
  await page.locator('input[name=start]').fill('2123-01-15')
  await page.locator('input[name=start_time]').fill('15:31')
  await page.locator('input[name=end]').fill('2123-01-17')
  await page.locator('[name=category]').selectOption({ index: 2 })
  await page.locator('[name=program]').selectOption({ label: 'Akce příroda' })
  await pickFromReactSelect(page, 3, ['ArrowDown', 'Enter'])

  await next(page)
  await page.locator('input[name=intended_for][value="3"]').check()

  await next(page)
  await pickFromReactSelect(
    page,
    5,
    ['ArrowDown', 'ArrowDown', 'Enter'],
    'Location 3',
  )

  await next(page)
  await page
    .locator('[name="propagation.is_shown_on_web"][value="false"]')
    .check()
  await page.locator('[name=registrationMethod][value="none"]').check()

  await next(page)
  // the react-select is partially covered by the "previous step" arrow
  await pickFromReactSelect(
    page,
    7,
    ['ArrowDown', 'ArrowDown', 'ArrowDown', 'Enter'],
    'displayname2',
    { force: true },
  )

  await page.locator('[placeholder=DD]').fill('29')
  await page.locator('[placeholder=MM]').fill('02')
  await page.locator('[placeholder=RRRR]').fill('2000')
  await mockUnknownUser(page, [
    { year: 2020 },
    { year: 2021 },
    { year: 2022 },
    { year: 2023 },
    { year: 2123 },
  ])
  await page
    .locator('[type=submit]', { hasText: /Pokračovat|Pokračuj/ })
    .first()
    .click()

  // main_organizer needs a React render cycle to appear in form data
  await page.waitForTimeout(100)
}

const fillPropagationFields = async (page: Page) => {
  await page.locator('button', { hasText: 'přihlášení' }).first().click()
  await page
    .locator('[name="propagation.is_shown_on_web"][value="true"]')
    .check()

  await page
    .locator('button', { hasText: 'info pro účastníky' })
    .first()
    .click()
  await page.locator('input[name="propagation.cost"]').fill('0')
  await page.locator('input[name="propagation.minimum_age"]').fill('0')
  await page.locator('input[name="propagation.maximum_age"]').fill('120')

  await page.locator('button', { hasText: 'pozvánka' }).first().click()
  await fillRichText(page, 'propagation.invitation_text_introduction', 'foo')
  await fillRichText(
    page,
    'propagation.invitation_text_practical_information',
    'bar',
  )

  await page
    .locator('button', { hasText: 'organizátorský tým' })
    .first()
    .click()
  await page
    .locator('input[name="propagation.organizers"]')
    .fill('nickname, name and otherName')
  await page
    .locator('input[name="propagation.contact_name"]')
    .fill('contact name')
  await page
    .locator('input[name="propagation.contact_email"]')
    .fill('asdf@example.com')
}

test.describe('create event', () => {
  test.beforeEach(async ({ page }) => {
    await mockCategories(page)
    await mockCurrentUser(page)

    await mock(
      page,
      { method: 'GET', pathname: '/api/web/administration_units/*' },
      {
        body: {
          results: [
            {
              id: 1,
              name: 'Aeiou',
              category: { id: 1, name: 'ZC', slug: 'zc' },
            },
          ],
        },
      },
    )
    await mock(
      page,
      { method: 'GET', pathname: '/api/frontend/locations/' },
      { body: { results: locations } },
    )
    await mock(
      page,
      { method: 'GET', pathname: '/api/frontend/search_users/' },
      request => {
        const search = (
          new URL(request.url()).searchParams.get('search') ?? ''
        ).toLowerCase()
        return {
          body: {
            results: searchUsers
              .filter(user =>
                (
                  user.display_name +
                  user.first_name +
                  user.last_name +
                  user.nickname
                )
                  .toLowerCase()
                  .includes(search),
              )
              .slice(5),
          },
        }
      },
    )
    await mock(
      page,
      { method: 'GET', pathname: '/api/frontend/users/' },
      { body: { results: [] } },
    )
  })

  test('can fill form and send data to create a new event', async ({
    page,
  }) => {
    await page.goto('/org/akce/vytvorit')
    await expectPath(page, '/org/akce/vytvorit')

    await page.locator('label[for=other]').click()
    await next(page)

    await page.locator('input[name=name]').fill('Event Name III')
    await page.locator('input[name=start]').fill('2123-01-15')
    await page.locator('input[name=start_time]').fill('15:31')
    await page.locator('input[name=end]').fill('2123-01-17')
    await page.locator('[name=category]').selectOption({ index: 2 })
    await page.locator('[name=program]').selectOption({ label: 'Akce příroda' })
    await pickFromReactSelect(page, 3, ['ArrowDown', 'Enter'])

    await next(page)
    await page.locator('input[name=intended_for][value="3"]').check()

    await next(page)
    await pickFromReactSelect(
      page,
      5,
      ['ArrowDown', 'ArrowDown', 'Enter'],
      'Location 3',
    )

    await next(page)
    await page
      .locator('[name="propagation.is_shown_on_web"][value="true"]')
      .check()
    await page.locator('[name=registrationMethod][value="none"]').check()

    await next(page)
    await page.locator('[name="propagation.cost"]').fill('10/100/1000')
    await page.locator('[name="propagation.minimum_age"]').fill('12')
    await page.locator('[name="propagation.maximum_age"]').fill('120')

    await next(page)
    await fillRichText(
      page,
      'propagation.invitation_text_introduction',
      'intro',
    )
    await fillRichText(
      page,
      'propagation.invitation_text_practical_information',
      'practical information',
    )

    await page
      .locator('[name="main_image.image"]')
      .setInputFiles(asset('image.png'))
    await addImage(page)
    await expect(page.locator('[name="images.0.image"]')).toBeAttached()
    await addImage(page)
    await expect(page.locator('[name="images.1.image"]')).toBeAttached()

    await next(page)
    await pickFromReactSelect(
      page,
      7,
      ['ArrowDown', 'ArrowDown', 'ArrowDown', 'Enter'],
      'displayname2',
    )

    await page.locator('[placeholder=DD]').fill('29')
    await page.locator('[placeholder=MM]').fill('02')
    await page.locator('[placeholder=RRRR]').fill('2000')
    await mockUnknownUser(page, [{ year: 2123 }])
    await page
      .locator('[type=submit]', { hasText: /Pokračovat|Pokračuj/ })
      .first()
      .click()

    await page
      .locator('input[name="propagation.contact_name"]')
      .fill('contact name')
    await page
      .locator('input[name="propagation.contact_email"]')
      .fill('asdf@example.com')

    const createEvent = await mock(
      page,
      { method: 'POST', pathname: '/api/frontend/events/' },
      { body: { id: 1 } },
    )
    await mock(page, {
      method: 'POST',
      pathname: '/api/frontend/events/1/propagation/images/',
    })
    await mock(page, {
      method: 'POST',
      pathname: '/api/frontend/events/1/questionnaire/questions/',
    })
    await mock(page, {
      method: 'POST',
      pathname: '/api/frontend/events/1/feedback_form/inquiries/',
    })

    await submit(page)

    expect((await createEvent.first()).body).toHaveProperty('name')
    await expectPath(page, '/org/akce/1')
  })

  test('shows validation errors', async ({ page }) => {
    await page.goto('/org/akce/vytvorit')
    await expectPath(page, '/org/akce/vytvorit')

    await submit(page)

    await expectPath(page, '/org/akce/vytvorit')
    await expectText(page, 'Opravte, prosím, chyby ve validaci')
  })

  test('can clone event', async ({ page }) => {
    await mockFullEvent(page)
    await page.goto('/org/akce/vytvorit?klonovat=1000')

    await next(page)
    await page.locator('input[name=start]').fill('2123-01-15')
    await page.locator('input[name=end]').fill('2123-01-17')

    const createEvent = await mock(
      page,
      { method: 'POST', pathname: '/api/frontend/events/' },
      { body: { id: 1000 } },
    )
    await mock(page, {
      method: 'POST',
      pathname: '/api/frontend/events/1000/propagation/images/',
    })
    await mock(page, {
      method: 'POST',
      pathname: '/api/frontend/events/1000/questionnaire/questions/',
    })

    await submit(page)

    const { body } = await createEvent.first()
    expect(body).not.toHaveProperty('is_canceled')
    expect(body).not.toHaveProperty('is_archived')
    expect(body).not.toHaveProperty('is_closed')
    expect(body).toMatchObject({ record: null, finance: null })
  })

  test('shows api error message', async ({ page }) => {
    await mockFullEvent(page)
    await page.goto('/org/akce/vytvorit?klonovat=1000')
    await next(page)

    await page.locator('input[name=start]').fill('2123-01-15')
    await page.locator('input[name=end]').fill('2123-01-17')

    const createEvent = await mock(
      page,
      { method: 'POST', pathname: '/api/frontend/events/' },
      {
        status: 400,
        body: {
          name: ['Toto pole nesmí být prázdné.'],
          group: [
            'Chybný typ. Byl přijat typ dict místo hodnoty primárního klíče.',
          ],
          record: { total_hours_worked: ['Je vyžadováno celé číslo.'] },
        },
      },
    )
    await mock(page, {
      method: 'POST',
      pathname: '/api/frontend/events/1000/propagation/images/',
    })

    await submit(page)
    await createEvent.first()

    await expect(
      page.getByText('Toto pole nesmí být prázdné').first(),
    ).toBeVisible()
    await page.locator('input[name=start]').fill('2123-01-15')
    await page.locator('input[name=end]').fill('2123-01-17')

    const createEvent2 = await mock(
      page,
      { method: 'POST', pathname: '/api/frontend/events/' },
      {
        status: 400,
        body: [
          'Toto pole nesmí být prázdné.',
          'Chybný typ. Byl přijat typ dict místo hodnoty primárního klíče.',
          'Je vyžadováno celé číslo.',
        ],
      },
    )

    await submit(page)
    await createEvent2.first()
  })

  test.describe('selecting standard registration form', () => {
    test.beforeEach(async ({ page }) => {
      await mockFullEvent(page, 27, 'simpleEvent')
      await page.goto('/org/akce/vytvorit?klonovat=27')
      await next(page)

      await page.locator('input[name=start]').fill('2123-01-15')
      await page.locator('input[name=end]').fill('2123-01-17')

      await fillPropagationFields(page)
      await page.locator('button', { hasText: 'přihlášení' }).first().click()
      await page.locator('[name=registrationMethod][value="standard"]').check()

      await mock(page, {
        method: 'POST',
        pathname: '/api/frontend/events/27/propagation/images/',
      })
    })

    test('should save correct intro and after questionnaire text', async ({
      page,
    }) => {
      const createEvent = await mock(
        page,
        { method: 'POST', pathname: '/api/frontend/events/' },
        { body: { id: 27 } },
      )
      await page
        .locator('[name="registration.questionnaire.introduction"]')
        .fill('foo')
      await page
        .locator('[name="registration.questionnaire.after_submit_text"]')
        .fill('bar')

      await submit(page)

      expect(
        (await createEvent.first()).body.registration.questionnaire,
      ).toEqual({
        introduction: 'foo',
        after_submit_text: 'bar',
      })
    })

    test('should save correct empty intro and after questionnaire text', async ({
      page,
    }) => {
      const createEvent = await mock(
        page,
        { method: 'POST', pathname: '/api/frontend/events/' },
        { body: { id: 27 } },
      )

      await submit(page)

      expect(
        (await createEvent.first()).body.registration.questionnaire,
      ).toEqual({
        introduction: '',
        after_submit_text: '',
      })
    })

    test('should allow adding registration form questions and save it to api', async ({
      page,
    }) => {
      const createEvent = await mock(
        page,
        { method: 'POST', pathname: '/api/frontend/events/' },
        { body: { id: 27 } },
      )
      const createQuestion = await mock(page, {
        method: 'POST',
        pathname:
          '/api/frontend/events/27/registration/questionnaire/questions/',
      })

      const addQuestion = page
        .locator('button', { hasText: 'Přidat otázku' })
        .first()

      await addQuestion.click()
      await page.locator('[name="questions.0.question"]').fill('Otázka 1')
      await page.locator('[name="questions.0.is_required"]').check()

      await addQuestion.click()
      await page.locator('[name="questions.1.question"]').fill('Otázka 2')
      await page
        .locator('[name="questions.1.data.type"]')
        .selectOption('checkbox')
      const addOption = page.locator('button', { hasText: 'Přidat možnost' })
      await expect(addOption).toHaveCount(1)
      await addOption.click()
      await expect(
        page.locator('[name^="questions.1.data.options"]'),
      ).toHaveCount(2)

      await page
        .locator('[name="questions.1.data.options.0.option"]')
        .fill('Option 1')
      await page
        .locator('[name="questions.1.data.options.1.option"]')
        .fill('Option 2')

      await addQuestion.click()
      await page.locator('[name="questions.2.question"]').fill('Otázka 3')
      await page.locator('[name="questions.2.is_required"]').check()
      await page.locator('[name="questions.2.data.type"]').selectOption('radio')
      await expect(addOption).toHaveCount(2)
      await addOption.last().click()
      await addOption.last().click()
      await page
        .locator('[name="questions.2.data.options.0.option"]')
        .fill('Radio option 1')
      await page
        .locator('[name="questions.2.data.options.1.option"]')
        .fill('Radio option 2')
      await page
        .locator('[name="questions.2.data.options.2.option"]')
        .fill('Radio option 3')

      await submit(page)

      await createEvent.first()

      const bodies = (await createQuestion.all(3)).map(call => call.body)
      expect(bodies).toContainEqual({
        question: 'Otázka 1',
        data: { type: 'text' },
        is_required: true,
        order: 0,
      })
      expect(bodies).toContainEqual({
        question: 'Otázka 2',
        data: {
          type: 'checkbox',
          options: [{ option: 'Option 1' }, { option: 'Option 2' }],
        },
        is_required: false,
        order: 1,
      })
      expect(bodies).toContainEqual({
        question: 'Otázka 3',
        data: {
          type: 'radio',
          options: [
            { option: 'Radio option 1' },
            { option: 'Radio option 2' },
            { option: 'Radio option 3' },
          ],
        },
        is_required: true,
        order: 2,
      })
    })
  })

  test.describe('selecting alternative registration form', () => {
    test.beforeEach(async ({ page }) => {
      await mockFullEvent(page)
      await page.goto('/org/akce/vytvorit?klonovat=1000')
      await next(page)

      await page.locator('input[name=start]').fill('2123-01-15')
      await page.locator('input[name=end]').fill('2123-01-17')

      await page.locator('button', { hasText: 'přihlášení' }).first().click()
    })

    test('should allow selecting the option, filling link, and submitting', async ({
      page,
    }) => {
      await page.locator('[name=registrationMethod][value="other"]').check()

      await page
        .locator('[name="registration.alternative_registration_link"]')
        .fill('https://example.com/some/link')

      const createEvent = await mock(
        page,
        { method: 'POST', pathname: '/api/frontend/events/' },
        { body: { id: 1000 } },
      )

      await submit(page)

      expect((await createEvent.first()).body).toMatchObject({
        registration: {
          is_registration_required: true,
          is_event_full: false,
          alternative_registration_link: 'https://example.com/some/link',
          questionnaire: null,
        },
      })
    })

    test('[link not filled] should fail with validation error', async ({
      page,
    }) => {
      await page.locator('[name=registrationMethod][value="other"]').check()
      await page
        .locator('[name="registration.alternative_registration_link"]')
        .click()

      await submit(page)

      await expect(
        page.locator('[class^=SystemMessage-module__header]'),
      ).toContainText('chyby ve validaci')
      await expect(
        page.locator('[class^=SystemMessage-module__detail]'),
      ).toContainText(
        'Alternativní odkaz pro registraci na akci: Toto pole je povinné',
      )
    })

    test('[link not valid url] should fail with validation error', async ({
      page,
    }) => {
      await page.locator('[name=registrationMethod][value="other"]').check()
      await page
        .locator('[name="registration.alternative_registration_link"]')
        .fill('hello')

      await submit(page)

      await expect(
        page.locator('[class^=SystemMessage-module__header]'),
      ).toContainText('chyby ve validaci')
      await expect(
        page.locator('[class^=SystemMessage-module__detail]'),
      ).toContainText(
        'Alternativní odkaz pro registraci na akci: Zadejte platný odkaz',
      )
    })

    test('should fill the form properly with default data', async ({
      page,
    }) => {
      const event = fixture('event')
      event.registration = {
        is_registration_required: true,
        is_event_full: false,
        alternative_registration_link: 'https://example.com/registration',
        questionnaire: null,
      }
      await mock(
        page,
        { method: 'GET', pathname: '/api/frontend/events/1000/' },
        { body: event },
      )
      await page.reload()

      await expect(
        page.locator('[name=registrationMethod][value=other]'),
      ).toBeChecked()
      await expect(
        page.locator('[name="registration.alternative_registration_link"]'),
      ).toHaveValue('https://example.com/registration')
    })
  })

  test.describe('organizer team and creator', () => {
    test('user should be pre-filled in team', async ({ page }) => {
      await fillForm(page)
      await expect(
        page.locator('[class^=FormInputError-module__inputWrapper]', {
          has: page.locator('[name=other_organizers]'),
        }),
      ).toContainText('Nickname (FirstName LastName)')
    })

    test.describe('user is organizer', () => {
      test('should show validation error when they are not part of team', async ({
        page,
      }) => {
        await fillForm(page)
        // remove pre-filled organizer (self)
        await page.locator('[aria-label^=Remove][role=button]').last().click()

        await submit(page)

        await expect(
          page.locator('[class^=SystemMessage-module__header]'),
        ).toContainText('chyby ve validaci')
        await expect(
          page.locator('[class^=SystemMessage-module__detail]'),
        ).toContainText('Musíš být v organizátorském týmu.')
      })

      test('should save event when user is part of organization team', async ({
        page,
      }) => {
        await fillForm(page)
        await expect(
          page.locator('[class^=FormInputError-module__inputWrapper]', {
            has: page.locator('[name=other_organizers]'),
          }),
        ).toContainText('Nickname (FirstName LastName)')

        const createEvent = await mock(
          page,
          { method: 'POST', pathname: '/api/frontend/events/' },
          { body: { id: 1000 } },
        )

        await submit(page)

        await createEvent.first()
      })
    })

    test.describe('user is administration unit', () => {
      test.beforeEach(async ({ page }) => {
        await mockCurrentUser(page, { fixture: 'chairman' })
      })

      test('should save even when they are not in team', async ({ page }) => {
        await fillForm(page)

        // remove pre-filled organizer (self)
        await page.locator('[aria-label^=Remove][role=button]').last().click()

        const createEvent = await mock(
          page,
          { method: 'POST', pathname: '/api/frontend/events/' },
          { body: { id: 1000 } },
        )

        await submit(page)

        await createEvent.first()
      })
    })
  })

  // Date validation rules (before/after March, admin override, etc.) are
  // unit tested in src/utils/__tests__/helpers.test.ts
  // (getEventCannotBeOlderThan, shouldBeFinishedUntil)
  // Error display from 400 responses is covered by "shows api error message" above.
})
