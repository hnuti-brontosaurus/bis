import type { Locator, Page } from '@playwright/test'
import { merge } from 'lodash'
import { asset, fixture, mock, type Recorder } from './support/api'
import { mockCategories, mockCurrentUser, mockFullEvent } from './support/mocks'
import { expect, expectText, test } from './support/test'

const participantsExample = fixture('eventParticipants')
const newUserExample = fixture('newUser')

/** Playwright has no `closest()`; the reverse xpath axis picks the nearest match. */
const closest = (locator: Locator, className: string) =>
  locator.locator(
    `xpath=ancestor-or-self::*[contains(@class, "${className}")][1]`,
  )

const participantRows = (page: Page) =>
  page.locator('table[class^=ParticipantsStep-module__table] tbody tr')

const importedRows = (page: Page) =>
  page.locator(
    '[class^=ImportParticipantsList-module__container] table tbody tr',
  )

const openParticipantsStep = async (page: Page, label: string) => {
  await page.goto('/org/akce/1000/uzavrit')
  await page.locator('label', { hasText: label }).first().click()
  await page.locator('button', { hasText: 'Pokračovat' }).first().click()
}

const selectExcel = (page: Page, label: string, file: string) =>
  page
    .locator('label', { hasText: label })
    .first()
    .locator('input[type=file]')
    .setInputFiles(asset(file))

test.describe('Close event - evidence and participants', () => {
  test.beforeEach(async ({ page }) => {
    await mockCurrentUser(page)

    await mockCategories(page)
    await mockFullEvent(page)
    // intercept also downloading photos and receipts
    await mock(
      page,
      { method: 'GET', pathname: '/api/frontend/events/*/record/photos/' },
      { body: { results: [] } },
    )
    await mock(
      page,
      {
        method: 'GET',
        pathname: '/api/frontend/events/*/record/attendance_list_pages/',
      },
      { body: { results: [] } },
    )
    await mock(
      page,
      { method: 'GET', pathname: '/api/frontend/events/*/finance/receipts/' },
      { body: { results: [] } },
    )
  })

  test.describe('ParticipantsStep component', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/org/akce/1000/uzavrit')
    })

    test('should show the participant input type options', async ({ page }) => {
      await expect(
        page.locator('[name="record.participantInputType"]'),
      ).toHaveCount(3)
    })

    test('should show the participant input type options with proper labels', async ({
      page,
    }) => {
      await expectText(page, 'Mám jen počet účastníků')
      await expectText(page, 'Mám jen jméno + příjmení + email')
      await expectText(page, 'Mám všechny informace')
    })

    test('should open modal on second Click', async ({ page }) => {
      await page.getByText('Mám jen počet účastníků').click()
      await page.getByText('Mám jen jméno + příjmení + email').click()
      await expectText(page, 'Měníš způsob registrace účastníků')
    })
  })

  test.describe('Simple participants list (contacts)', () => {
    test.describe('Import of simple participants list from xls', () => {
      test('should load xls data to participants list form', async ({
        page,
      }) => {
        await openParticipantsStep(page, 'Mám jen jméno + příjmení + email')

        await selectExcel(page, 'Importovat seznam', 'simple-participants.xlsx')

        const rows = participantRows(page)
        await expect(rows).toHaveCount(4)

        const cells = rows.last().locator('td')
        await expect(cells.nth(0).locator('input')).toHaveValue('Petr')
        await expect(cells.nth(1).locator('input')).toHaveValue('Pan')
        await expect(cells.nth(2).locator('input')).toHaveValue(
          'petr.pan@example.com',
        )
        await expect(cells.nth(3).locator('input')).toHaveValue('761001002')
      })
    })
  })

  test.describe('Full participant list', () => {
    let updateEvent: Recorder
    let suggestAddress: Recorder

    test.beforeEach(async ({ page }) => {
      // make sure we have a few participants to show
      await mock(
        page,
        {
          method: 'GET',
          pathname: '/api/frontend/events/1000/record/participants/',
        },
        { fixture: 'eventParticipants' },
      )

      updateEvent = await mock(page, {
        method: 'PATCH',
        pathname: '/api/frontend/events/1000/',
      })
      suggestAddress = await mock(
        page,
        { method: 'GET', url: /^https:\/\/api\.mapy\.cz\/v1\/suggest\?/ },
        {
          body: {
            items: [
              {
                name: 'Hvězdová 303/4',
                label: 'Adresa',
                position: { lon: 16.62287, lat: 49.20063 },
                bbox: [
                  16.620062420875346, 49.199532900919216, 16.625676891401096,
                  49.20173403915781,
                ],
                type: 'regional.address',
                location: 'Brno - Zábrdovice, Česko',
                regionalStructure: [
                  { name: '303/4', type: 'regional.address' },
                  { name: 'Hvězdová', type: 'regional.street' },
                  { name: 'Zábrdovice', type: 'regional.municipality_part' },
                  { name: 'Brno-sever', type: 'regional.municipality_part' },
                  { name: 'Brno', type: 'regional.municipality' },
                  { name: 'okres Brno-město', type: 'regional.region' },
                  { name: 'Jihomoravský kraj', type: 'regional.region' },
                  { name: 'Česko', type: 'regional.country', isoCode: 'CZ' },
                ],
                zip: '602 00',
              },
            ],
            locality: [],
          },
        },
      )
    })

    const fillAddress = async (page: Page, name: string) => {
      const before = suggestAddress.calls.length
      const select = closest(
        page.locator(`[name="${name}"]`),
        'AddressSubform-module__select',
      )
      await select
        .locator('[class*=control] [class*=Input] input')
        .pressSequentially('Hvězdová 4')
      await suggestAddress.nth(before)
      await closest(
        page.locator(`[name="${name}"]`),
        'AddressSubform-module__select',
      )
        .locator('[class*=MenuList] [class*=option]')
        .nth(0)
        .click()
    }

    test.describe('Adding non-existent user as participant', () => {
      const visitPage = (page: Page) =>
        openParticipantsStep(page, 'Mám všechny informace')

      const clickAddNewParticipant = (page: Page) =>
        page
          .locator('button', { hasText: 'Přidat nového účastníka' })
          .first()
          .click()

      const fillUserForm = async (page: Page) => {
        await page.locator('input[name=first_name]').fill('first_name')
        await page.locator('input[name=last_name]').fill('last_name')
        await page.locator('[placeholder=DD]').fill('01')
        await page.locator('[placeholder=MM]').fill('01')
        await page.locator('[placeholder=RRRR]').fill('1950')
        await page.locator('[name=email]').fill('test@example.com')
        await fillAddress(page, 'address.street')

        // debounce is 0ms under e2e, form persists immediately
      }

      const newParticipantModal = (page: Page) =>
        page
          .locator('[class^=StyledModal]')
          .filter({ hasText: 'Nový účastník' })

      const closeOwlGuide = (page: Page) =>
        page.locator('div[id="closeOwlGuide"]').click()

      test('filling address also fills city and zip code', async ({ page }) => {
        await visitPage(page)
        await clickAddNewParticipant(page)
        await fillAddress(page, 'address.street')

        await expect(page.locator('[name="address.city"]')).toHaveValue('Brno')
        await expect(page.locator('[name="address.zip_code"]')).toHaveValue(
          '60200',
        )
      })

      test('should open a modal, receive data of new user, and save them as a participant', async ({
        page,
      }) => {
        await visitPage(page)
        await clickAddNewParticipant(page)

        await expect(newParticipantModal(page).first()).toBeAttached()
        await fillUserForm(page)

        await closeOwlGuide(page)

        const createUser = await mock(
          page,
          { method: 'POST', pathname: '/api/frontend/users/' },
          { fixture: 'newUser' },
        )
        await page
          .locator('[type=submit]', { hasText: 'Potvrdit' })
          .first()
          .click()

        expect((await createUser.first()).body).toEqual({
          first_name: 'first_name',
          last_name: 'last_name',
          nickname: '',
          birth_name: '',
          subscribed_to_newsletter: true,
          health_insurance_company: null,
          health_issues: '',
          email: 'test@example.com',
          birthday: '1950-01-01',
          address: {
            street: 'Hvězdová 303/4',
            city: 'Brno',
            zip_code: '60200',
          },
          contact_address: null,
          close_person: null,
          donor: null,
          offers: null,
          phone: '',
          eyca_card: null,
        })

        expect((await updateEvent.first()).body).toEqual({
          record: {
            participants: [
              ...participantsExample.results.map((p: { id: string }) => p.id),
              newUserExample.id,
            ],
            contacts: [],
            number_of_participants: null,
            number_of_participants_under_26: null,
          },
        })

        await expect(newParticipantModal(page)).toHaveCount(0)

        // afterwards, the modal should be cleared
        await clickAddNewParticipant(page)
        await expect(newParticipantModal(page).first()).toBeAttached()
        await expect(page.locator('[name=first_name]')).toHaveValue('')
      })

      test('[empty email] should send email: null to backend', async ({
        page,
      }) => {
        await visitPage(page)
        await clickAddNewParticipant(page)
        await fillUserForm(page)
        await page.locator('[name=email]').fill('')

        await closeOwlGuide(page)

        const createUser = await mock(
          page,
          { method: 'POST', pathname: '/api/frontend/users/' },
          { fixture: 'newUser' },
        )
        await page
          .locator('[type=submit]', { hasText: 'Potvrdit' })
          .first()
          .click()

        expect((await createUser.first()).body.email).toBeNull()
        await updateEvent.first()
      })

      test('[api error] should show error and keep modal open', async ({
        page,
      }) => {
        await visitPage(page)
        await clickAddNewParticipant(page)

        await expect(newParticipantModal(page).first()).toBeAttached()
        await fillUserForm(page)

        await closeOwlGuide(page)

        await mock(
          page,
          { method: 'POST', pathname: '/api/frontend/users/' },
          { status: 400 },
        )
        await page
          .locator('[type=submit]', { hasText: 'Potvrdit' })
          .first()
          .click()

        await expect(
          page.locator('div').filter({ hasText: 'Něco se nepovedlo' }).last(),
        ).toBeVisible()

        await page.waitForTimeout(100)
        await expect(newParticipantModal(page).first()).toBeAttached()
      })

      test('should keep data in form after leaving and returning', async ({
        page,
      }) => {
        await visitPage(page)
        await clickAddNewParticipant(page)

        await expect(newParticipantModal(page).first()).toBeAttached()
        await fillUserForm(page)

        await page.keyboard.press('Escape')
        await expect(newParticipantModal(page)).toHaveCount(0)

        await clickAddNewParticipant(page)

        await expect(page.locator('[name=first_name]')).toHaveValue(
          'first_name',
        )
      })

      test('should clear form when clicking Cancel', async ({ page }) => {
        await visitPage(page)
        await clickAddNewParticipant(page)

        await expect(newParticipantModal(page).first()).toBeAttached()
        await fillUserForm(page)

        await closeOwlGuide(page)

        await page
          .locator('[class^=StyledModal] [type=reset]', { hasText: 'Zrušit' })
          .first()
          .click()
        await expect(newParticipantModal(page)).toHaveCount(0)

        await clickAddNewParticipant(page)
        await expect(page.locator('[name=first_name]')).toHaveValue('')
      })
    })

    test('[when clicking remove] should ask for confirmation and remove participant', async ({
      page,
    }) => {
      await openParticipantsStep(page, 'Mám všechny informace')

      await page
        .locator('button[aria-label="Smazat účastníka Jana Novak"]')
        .click()

      await expectText(
        page,
        'Opravdu chcete smazat účastnici/účastníka Jana Novak z akce Event Name?',
      )

      await page
        .locator('button[class*=danger]', { hasText: 'Ano' })
        .first()
        .click()

      const participants = (await updateEvent.first()).body.record.participants
      expect(participants).toContain('11111111-1111-1111-1111-111111111111')
      expect(participants).not.toContain('00000000-1111-2222-3333-444444444444')
    })

    test('[when clicking update] should open user edit form, and save after editing', async ({
      page,
    }) => {
      await openParticipantsStep(page, 'Mám všechny informace')

      await page.locator('div[id="closeOwlGuide"]').click()

      await page
        .locator('button[aria-label="Upravit účastníka Jana Novak"]')
        .click()

      await expectText(page, 'Úprava dat účastnice/účastníka Jana Novak')
      await expect(page.locator('[name="last_name"]')).toHaveValue('Novak')

      await expect(page.locator('[name="first_name"]')).toHaveValue('Jana')
      await page.locator('[name="first_name"]').fill('Dana')

      await fillAddress(page, 'address.street')
      await page.locator('[name="address.city"]').fill('NewTown')
      await page.locator('[name="address.zip_code"]').fill('12345')
      await page
        .locator('[name=health_insurance_company]')
        .selectOption({ index: 4 })

      const updateUser = await mock(page, {
        method: 'PATCH',
        pathname: '/api/frontend/users/*/',
      })
      await page
        .locator('[type=submit]', { hasText: 'Potvrdit' })
        .first()
        .click()

      const call = await updateUser.first()
      expect(call.body).toMatchObject({
        first_name: 'Dana',
        address: {
          street: 'Hvězdová 303/4',
          city: 'NewTown',
          zip_code: '12345',
        },
        health_insurance_company: 4,
      })
      expect(call.url).toContain(
        '/api/frontend/users/00000000-1111-2222-3333-444444444444',
      )
      expect(call.method).toBe('PATCH')
    })

    test.describe.skip('Import full participants from excel', () => {
      let categories: Awaited<ReturnType<typeof mockCategories>>

      test.beforeEach(async ({ page }) => {
        categories = await mockCategories(page)
        await openParticipantsStep(page, 'Mám všechny informace')
      })

      test('[existent users] should import data, save the users as participants and show in table', async ({
        page,
      }) => {
        await expect(participantRows(page)).toHaveCount(4)

        await mock(
          page,
          {
            method: 'GET',
            url: /get_unknown_user\/\?birthday=1993-03-01&first_name=Jana&last_name=Nov%C3%A1kov%C3%A1/,
          },
          { fixture: 'user1' },
        )
        await mock(
          page,
          {
            method: 'GET',
            url: /get_unknown_user\/\?birthday=1995-05-12&first_name=Dan&last_name=Nov%C3%A1k/,
          },
          { fixture: 'user2' },
        )

        await selectExcel(page, 'Importovat z excelu', 'full-participants.xlsx')

        await expect(importedRows(page)).toHaveCount(2)
        await expect(
          importedRows(page).locator('[title="Uživatel/ka existuje"]'),
        ).toHaveCount(2)

        const participants = fixture('eventParticipants')
        await mock(
          page,
          {
            method: 'GET',
            pathname: '/api/frontend/events/1000/record/participants/',
          },
          {
            body: merge(participants, {
              results: [
                ...participants.results,
                fixture('user1'),
                fixture('user2'),
              ],
            }),
          },
        )

        await page
          .locator('[class^=ImportParticipantsList-module__container] button', {
            hasText: 'Přidat do seznamu',
          })
          .first()
          .click()

        await expect(participantRows(page)).toHaveCount(6)
      })

      test('[non-existent users] should import data, create users and save them as participants', async ({
        page,
      }) => {
        await expect(participantRows(page)).toHaveCount(4)

        await mock(
          page,
          {
            method: 'GET',
            url: /get_unknown_user\/\?birthday=1993-03-01&first_name=Jana&last_name=Nov%C3%A1kov%C3%A1/,
          },
          { status: 404 },
        )
        await mock(
          page,
          {
            method: 'GET',
            url: /get_unknown_user\/\?birthday=1995-05-12&first_name=Dan&last_name=Nov%C3%A1k/,
          },
          { status: 404 },
        )

        const createUser = await mock(
          page,
          { method: 'POST', pathname: '/api/frontend/users/' },
          { fixture: 'user2' },
          { times: 1 },
        )
        const createUser2 = await mock(
          page,
          { method: 'POST', pathname: '/api/frontend/users/' },
          { fixture: 'user1' },
          { times: 1 },
        )

        await selectExcel(page, 'Importovat z excelu', 'full-participants.xlsx')

        await expect(importedRows(page)).toHaveCount(2)
        await expect(
          importedRows(page).locator('[title="Uživatel/ka bude vytvořen/a"]'),
        ).toHaveCount(2)

        const participants = fixture('eventParticipants')
        const fetchParticipants = await mock(
          page,
          {
            method: 'GET',
            pathname: '/api/frontend/events/1000/record/participants/',
          },
          {
            body: merge(participants, {
              results: [
                ...participants.results,
                fixture('user1'),
                fixture('user2'),
              ],
            }),
          },
        )

        await page
          .locator('[class^=ImportParticipantsList-module__container] button', {
            hasText: 'Přidat do seznamu',
          })
          .first()
          .click()

        // these data should match those provided in e2e/assets/full-participants.xlsx
        const expectations = [
          {
            first_name: 'Dan',
            last_name: 'Novák',
            nickname: '',
            birth_name: '',
            pronoun: null,
            subscribed_to_newsletter: true,
            health_insurance_company: null,
            health_issues: '',
            email: 'dan.novak@example.com',
            phone: '',
            birthday: '1995-05-12',
            address: {
              street: 'Hlavní 5',
              city: 'Brno - střed',
              zip_code: '10100',
            },
            contact_address: null,
            close_person: null,
            donor: null,
            offers: null,
            eyca_card: null,
          },
          {
            first_name: 'Jana',
            last_name: 'Nováková',
            nickname: 'Julie',
            birth_name: 'Nová',
            pronoun: null,
            subscribed_to_newsletter: true,
            health_insurance_company: 3,
            health_issues: 'Jahody',
            email: 'jana.novakova@example.com',
            phone: '601001002',
            birthday: '1993-03-01',
            address: { street: 'Horní 50', city: 'Praha 6', zip_code: '16000' },
            contact_address: {
              street: 'Dolní 40',
              city: 'Praha 5',
              zip_code: '15000',
            },
            close_person: {
              first_name: 'Dana',
              last_name: 'Nováková',
              email: 'dana@example.com',
              phone: '602002003',
            },
            donor: null,
            offers: null,
            eyca_card: null,
          },
        ]

        const created = [
          ...(await createUser.all(1)),
          ...(await createUser2.all(1)),
        ]
        expect(
          created
            .map(call => call.body)
            .sort((a, b) => (a.first_name > b.first_name ? 1 : -1)),
        ).toEqual(expectations)

        // order is not certain, because of create-user stubs' uncertain order
        expect(
          (await updateEvent.first()).body.record.participants,
        ).toHaveLength(6)

        await fetchParticipants.first()

        await expect(participantRows(page)).toHaveCount(6)
      })

      test('should allow editing imported data', async ({ page }) => {
        await expect(participantRows(page)).toHaveCount(4)

        await mock(
          page,
          {
            method: 'GET',
            url: /get_unknown_user\/\?birthday=1993-03-01&first_name=Jana&last_name=Nov%C3%A1kov%C3%A1/,
          },
          { fixture: 'user1' },
        )
        await mock(
          page,
          {
            method: 'GET',
            url: /get_unknown_user\/\?birthday=1995-05-12&first_name=Dan&last_name=Nov%C3%A1k/,
          },
          { status: 404 },
        )

        await selectExcel(page, 'Importovat z excelu', 'full-participants.xlsx')

        await categories.health_insurance_companies.first()
        await page.waitForTimeout(100)

        const userRows = page.locator(
          '[class^=ImportParticipantsList-module__container] table tbody tr[class^=ImportParticipantsList-module__userRow]',
        )

        await expect(userRows).toHaveCount(2)
        await userRows.first().click()

        await expect(importedRows(page)).toHaveCount(3)
        const firstStreet = importedRows(page)
          .nth(1)
          .locator('input[name="address.street"]')
        await expect(firstStreet).toHaveValue('Horní 50')
        await firstStreet.fill('Rygol 123')
        await closest(firstStreet, 'ImportParticipantsList-module__container')
          .locator('form button', { hasText: 'Potvrdit' })
          .first()
          .click()

        await expect(userRows).toHaveCount(2)
        await userRows.last().click()

        const secondStreet = importedRows(page).locator(
          'input[name="address.street"]',
        )
        await expect(secondStreet).toHaveValue('Hlavní 5')
        await secondStreet.fill('asdfasdf 123')
        const secondForm = closest(
          secondStreet,
          'ImportParticipantsList-module__container',
        )
        await expect(secondForm.locator('input[name=nickname]')).toHaveValue('')
        await secondForm.locator('input[name=nickname]').fill('Jablko')
        await secondForm
          .locator('form button', { hasText: 'Potvrdit' })
          .first()
          .click()

        const createUser = await mock(
          page,
          { method: 'POST', pathname: '/api/frontend/users/' },
          { fixture: 'user1' },
          { times: 1 },
        )
        const updateUser = await mock(
          page,
          { method: 'PATCH', pathname: '/api/frontend/users/*/' },
          { fixture: 'user2' },
          { times: 1 },
        )

        await page
          .locator('[class^=ImportParticipantsList-module__container] button', {
            hasText: 'Přidat do seznamu',
          })
          .first()
          .click()

        expect((await createUser.first()).body).toEqual({
          first_name: 'Dan',
          last_name: 'Novák',
          nickname: 'Jablko',
          birth_name: '',
          subscribed_to_newsletter: true,
          health_insurance_company: null,
          health_issues: '',
          email: 'dan.novak@example.com',
          phone: '',
          birthday: '1995-05-12',
          address: {
            street: 'asdfasdf 123',
            city: 'Brno - střed',
            zip_code: '10100',
          },
          contact_address: null,
          close_person: null,
          donor: null,
          offers: null,
          eyca_card: null,
        })

        expect((await updateUser.first()).body).toEqual({
          first_name: 'Jana',
          last_name: 'Nováková',
          nickname: 'Julie',
          birth_name: 'Nová',
          subscribed_to_newsletter: true,
          health_insurance_company: 3,
          health_issues: 'Jahody',
          email: 'jana.novakova@example.com',
          phone: '601001002',
          birthday: '1993-03-01',
          address: {
            street: 'Rygol 123',
            city: 'Praha 6',
            zip_code: '16000',
          },
          contact_address: {
            street: 'Dolní 40',
            city: 'Praha 5',
            zip_code: '15000',
          },
          close_person: {
            first_name: 'Dana',
            last_name: 'Nováková',
            email: 'dana@example.com',
            phone: '602002003',
          },
          donor: null,
          offers: null,
          eyca_card: null,
        })
      })

      test.fixme('[invalid data] should show invalid rows highlighted', () => {
        // Deliberately unimplemented; kept so the gap shows up in the report.
      })
    })
  })
})
