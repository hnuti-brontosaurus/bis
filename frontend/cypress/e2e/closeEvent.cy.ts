import { merge } from 'lodash'
import * as participantsExample from '../fixtures/eventParticipants.json'
import * as newUserExample from '../fixtures/newUser.json'

describe('Close event - evidence and participants', () => {
  // sign in before each test
  beforeEach(() => {
    cy.interceptLogin()
    cy.login('asdf@example.com', 'correcthorsebatterystaple')
  })

  // stub the api calls to fetch event (it is one day event)
  beforeEach(() => {
    cy.interceptCategories()
    cy.interceptFullEvent()
    // intercept also downloading photos and receipts
    cy.intercept(
      { method: 'GET', pathname: '/api/frontend/events/*/record/photos/' },
      { results: [] },
    )
    cy.intercept(
      {
        method: 'GET',
        pathname: '/api/frontend/events/*/record/attendance_list_pages/',
      },
      { results: [] },
    )
    cy.intercept(
      { method: 'GET', pathname: '/api/frontend/events/*/finance/receipts/' },
      { results: [] },
    )
  })

  describe('ParticipantsStep component', () => {
    beforeEach(() => {
      cy.visit('/org/akce/1000/uzavrit')
    })

    it('should show the participant input type options', () => {
      cy.get('[name=record\\.participantInputType]').should('have.length', 3)
    })

    it('should show the participant input type options with proper labels', () => {
      cy.contains('Mám jen počet účastníků')
      cy.contains('Mám jen jméno + příjmení + email')
      cy.contains('Mám všechny informace')
    })

    it('should open modal on second Click', () => {
      cy.contains('Mám jen počet účastníků').click()
      cy.contains('Mám jen jméno + příjmení + email').click()
      cy.contains('Měníš způsob registrace účastníků')
    })
  })

  describe('Simple participants list (contacts)', () => {
    describe('Import of simple participants list from xls', () => {
      it('should load xls data to participants list form', () => {
        cy.visit('/org/akce/1000/uzavrit')

        cy.get('label:contains(Mám jen jméno + příjmení + email)')
          .should('be.visible')
          .click()
        cy.get('button:contains(Pokračuj)').click()

        cy.get('label:contains(Importovat seznam)')
          .should('be.visible')
          .selectFile('cypress/e2e/simple-participants.xlsx')

        cy.get('table[class^=ParticipantsStep_table] tbody tr')
          .should('have.length', 4)
          .last()
          .find('td')
          .first()
          .find('input')
          .should('have.value', 'Petr')
          .parent()
          .next()
          .find('input')
          .should('have.value', 'Pan')
          .parent()
          .next()
          .find('input')
          .should('have.value', 'petr.pan@example.com')
          .parent()
          .next()
          .find('input')
          .should('have.value', '761001002')
      })
    })
  })

  describe('Full participant list', () => {
    beforeEach(() => {
      // make sure we have a few participants to show
      cy.intercept(
        {
          method: 'GET',
          pathname: '/api/frontend/events/1000/record/participants/',
        },
        { fixture: 'eventParticipants' },
      )

      // intercept the updates of participants
      cy.intercept(
        { method: 'PATCH', pathname: '/api/frontend/events/1000/' },
        {},
      ).as('updateEvent')
    })

    describe('Adding non-existent user as participant', () => {
      // do the initial visiting and clicking to open user form modal
      const visitPage = () => {
        cy.visit('/org/akce/1000/uzavrit')

        cy.get('label:contains(Mám všechny informace)')
          .should('be.visible')
          .click()
        cy.get('button:contains(Pokračuj)').click()
      }

      const clickAddNewParticipant = () => {
        cy.get('button:contains(Přidej nového účastníka)')
          .should('be.visible')
          .click()
      }

      // check open form waiting for user data
      // and fill some data
      const fillUserForm = () => {
        cy.get('input[name=first_name]').should('be.visible').type('first_name')
        cy.get('input[name=last_name]').should('be.visible').type('last_name')
        cy.get('[placeholder=DD]').should('be.visible').type('01')
        cy.get('[placeholder=MM]').should('be.visible').type('01')
        cy.get('[placeholder=RRRR]').should('be.visible').type('1950')
        cy.get('[name=email]').type('test@example.com')
        cy.get('[name=address\\.street]').type('abc')
        cy.get('[name=address\\.city]').type('de')
        cy.get('[name=address\\.zip_code]').type('10000')

        // give form a chance to persist
        cy.wait(1000)
      }

      const checkForm = (exists: boolean) => {
        cy.get('[class^=StyledModal]:contains(Nový účastník)').should(
          exists ? 'exist' : 'not.exist',
        )
      }

      it('should open a modal, receive data of new user, and save them as a participant', () => {
        visitPage()
        clickAddNewParticipant()

        // we should be able to see an open form
        checkForm(true)
        // and to fill some data
        fillUserForm()

        // close helper
        cy.get('div[id="closeOwlGuide"]').click()

        // click Submit and succeed
        cy.intercept(
          { method: 'POST', pathname: '/api/frontend/users' },
          { fixture: 'newUser' },
        ).as('createUser')
        cy.get('[type=submit]:contains(Potvrdit)').click()

        // we should call create user with proper data
        cy.wait('@createUser')
          .its('request.body')
          .should('deep.equal', {
            first_name: 'first_name',
            last_name: 'last_name',
            nickname: '',
            birth_name: '',
            // pronoun: null,
            subscribed_to_newsletter: true,
            health_insurance_company: null,
            health_issues: '',
            email: 'test@example.com',
            birthday: '1950-01-01',
            address: {
              street: 'abc',
              city: 'de',
              zip_code: '10000',
            },
            contact_address: null,
            close_person: null,
            donor: null,
            offers: null,
            phone: '',
            eyca_card: null,
          })

        // and we should call update event with proper data
        cy.wait('@updateEvent')
          .its('request.body')
          .should('deep.equal', {
            record: {
              participants: [
                ...participantsExample.results.map(p => p.id),
                newUserExample.id,
              ],
              contacts: [],
              number_of_participants: null,
              number_of_participants_under_26: null,
            },
          })

        // the modal should be invisible at this point
        checkForm(false)

        // afterwards, the modal should be cleared
        clickAddNewParticipant()
        checkForm(true)
        cy.get('[name=first_name]').should('have.value', '')
      })

      it('[empty email] should send email: null to backend', () => {
        visitPage()
        clickAddNewParticipant()
        // fill data
        fillUserForm()
        // but keep the email empty
        cy.get('[name=email]').clear()

        // close helper
        cy.get('div[id="closeOwlGuide"]').click()

        // click Submit and succeed
        cy.intercept(
          { method: 'POST', pathname: '/api/frontend/users' },
          { fixture: 'newUser' },
        ).as('createUser')
        cy.get('[type=submit]:contains(Potvrdit)').click()

        // we should create user with email: null
        cy.wait('@createUser').its('request.body.email').should('be.null')
        // and call update event
        cy.wait('@updateEvent')
      })

      it('[api error] should show error and keep modal open', () => {
        visitPage()
        clickAddNewParticipant()

        // we should be able to see an open form
        checkForm(true)
        // and to fill some data
        fillUserForm()

        // close helper
        cy.get('div[id="closeOwlGuide"]').click()

        // click Submit and fail
        cy.intercept(
          { method: 'POST', pathname: '/api/frontend/users' },
          { statusCode: 400 },
        ).as('createUser')
        cy.get('[type=submit]:contains(Potvrdit)').click()

        // check that error is shown
        cy.get('div:contains(Něco se nepovedlo)').should('be.visible')

        // wait a bit and check that modal is still open
        cy.wait(1000)
        checkForm(true)
      })

      it('should keep data in form after leaving and returning', () => {
        visitPage()
        clickAddNewParticipant()

        // we should be able to see an open form
        checkForm(true)
        // and to fill some data
        fillUserForm()

        // leave
        cy.get('body').type('{esc}')
        checkForm(false)

        // return
        clickAddNewParticipant()

        cy.get('[name=first_name]').should('have.value', 'first_name')
      })

      it('should clear form when clicking Cancel', () => {
        visitPage()
        clickAddNewParticipant()

        // we should be able to see an open form
        checkForm(true)
        // and to fill some data
        fillUserForm()

        // close helper
        cy.get('div[id="closeOwlGuide"]').click()

        // then click cancel
        cy.get('[class^=StyledModal] [type=reset]:contains(Zrušit)').click()
        // the form should close
        checkForm(false)

        // and it should be empty after reopening
        clickAddNewParticipant()
        cy.get('[name=first_name]').should('have.value', '')
      })
    })

    it('[when clicking remove] should ask for confirmation and remove participant', () => {
      // go to participants page
      cy.visit('/org/akce/1000/uzavrit')

      cy.get('label:contains(Mám všechny informace)')
        .should('be.visible')
        .click()
      cy.get('button:contains(Pokračuj)').click()

      // click delete
      cy.get('button[aria-label="Smazat účastníka Jana Novak"]').click()

      // confirmation modal should open
      cy.contains(
        'Opravdu chcete smazat účastnici/účastníka Jana Novak z akce Event Name?',
      )

      // click Confirm (should be a danger button)
      cy.get('button[class*=danger]:contains(Ano)').click()

      // check that a proper request was sent to api
      cy.wait('@updateEvent')
        .its('request.body.record.participants')
        .should('contain', '11111111-1111-1111-1111-111111111111')
        .should('not.contain', '00000000-1111-2222-3333-444444444444')
    })

    it('[when clicking update] should open user edit form, and save after editing', () => {
      // go to participants page
      cy.visit('/org/akce/1000/uzavrit')

      cy.get('label:contains(Mám všechny informace)')
        .should('be.visible')
        .click()
      cy.get('button:contains(Pokračuj)').click()

      // close helper
      cy.get('div[id="closeOwlGuide"]').click()

      // click update participant
      cy.get('button[aria-label="Upravit účastníka Jana Novak"]').click()

      // a form with pre-filled participant's data should open
      cy.contains('Úprava dat účastnice/účastníka Jana Novak')
      cy.get('[name="last_name"]').should('have.value', 'Novak')

      // let's edit some data
      cy.get('[name="first_name"]')
        .should('have.value', 'Jana')
        .clear()
        .type('Dana')

      cy.get('[name=address\\.street]').clear().type('NewStreetName 42')
      cy.get('[name=address\\.city]').clear().type('NewTown')
      cy.get('[name=address\\.zip_code]').clear().type('12345')
      cy.get('[name=health_insurance_company]').select(4)

      // intercept the updates of user
      cy.intercept(
        { method: 'PATCH', pathname: '/api/frontend/users/*/' },
        {},
      ).as('updateUser')
      // submit
      cy.get('[type=submit]:contains(Potvrdit)').click()

      // a proper request should be sent to update user
      cy.wait('@updateUser').then(a => {
        expect(a.request.body).to.deep.include({
          first_name: 'Dana',
          address: {
            street: 'NewStreetName 42',
            city: 'NewTown',
            zip_code: '12345',
          },
          health_insurance_company: 4,
        })
        expect(a.request.url).to.contain(
          '/api/frontend/users/00000000-1111-2222-3333-444444444444',
        )
        expect(a.request.method).to.equal('PATCH')
      })
    })

    describe('Import full participants from excel', () => {
      beforeEach(() => {
        cy.visit('/org/akce/1000/uzavrit')

        cy.get('label:contains(Mám všechny informace)')
          .should('be.visible')
          .click()
        cy.get('button:contains(Pokračuj)').click()
      })

      it('[existent users] should import data, save the users as participants and show in table', () => {
        // at the beginning, the table has 4 rows
        cy.get('table[class^=ParticipantsStep_table] tbody tr').should(
          'have.length',
          4,
        )

        cy.intercept(
          {
            method: 'GET',
            path: '/api/frontend/get_unknown_user/?birthday=1993-03-01&first_name=Jana&last_name=Nov%C3%A1kov%C3%A1',
          },
          { fixture: 'user1' },
        )

        cy.intercept(
          {
            method: 'GET',
            path: '/api/frontend/get_unknown_user/?birthday=1995-05-12&first_name=Dan&last_name=Nov%C3%A1k',
          },
          { fixture: 'user2' },
        )

        cy.get('label:contains(Importovat z excelu)')
          .should('be.visible')
          .selectFile('cypress/e2e/full-participants.xlsx')

        // a table with imported users should appear
        // and after a while, indicate that users exist already
        cy.get('[class^=ImportParticipantsList_container] table tbody tr')
          .should('have.length', 2)
          .find('[title="Uživatel/ka existuje"]')
          .should('have.length', 2)

        // now, save button is shown, we click it and users show up in the main table
        cy.fixture('eventParticipants').then(participants => {
          cy.fixture('user1').then(user1 => {
            cy.fixture('user2').then(user2 => {
              cy.intercept(
                {
                  method: 'GET',
                  pathname: '/api/frontend/events/1000/record/participants/',
                },
                {
                  body: merge(participants, {
                    results: [...participants.results, user1, user2],
                  }),
                },
              )
            })
          })
        })

        cy.get('[class^=ImportParticipantsList_container]')
          .find('button')
          .contains('Přidat do seznamu')
          .click()

        // check that the users appear in the table
        cy.get('table[class^=ParticipantsStep_table] tbody tr').should(
          'have.length',
          6,
        )
      })

      it('[non-existent users] should import data, create users and save them as participants', () => {
        // at the beginning, the table has 4 rows
        cy.get('table[class^=ParticipantsStep_table] tbody tr').should(
          'have.length',
          4,
        )

        // click import button and select spreadsheet file
        cy.intercept(
          {
            method: 'GET',
            path: '/api/frontend/get_unknown_user/?birthday=1993-03-01&first_name=Jana&last_name=Nov%C3%A1kov%C3%A1',
          },
          { statusCode: 404 },
        )

        cy.intercept(
          {
            method: 'GET',
            path: '/api/frontend/get_unknown_user/?birthday=1995-05-12&first_name=Dan&last_name=Nov%C3%A1k',
          },
          { statusCode: 404 },
        )

        cy.intercept(
          { method: 'POST', pathname: '/api/frontend/users', times: 1 },
          { fixture: 'user2' },
        ).as('createUser')

        cy.intercept(
          { method: 'POST', pathname: '/api/frontend/users', times: 1 },
          { fixture: 'user1' },
        ).as('createUser')

        cy.get('label:contains(Importovat z excelu)')
          .should('be.visible')
          .selectFile('cypress/e2e/full-participants.xlsx')

        // a table with imported users should appear
        // and after a while, indicate that users don't exist yet
        cy.get('[class^=ImportParticipantsList_container] table tbody tr')
          .should('have.length', 2)
          .find('[title="Uživatel/ka bude vytvořen/a"]')
          .should('have.length', 2)

        // now, save button is shown, we click it and users show up in the main table
        cy.fixture('eventParticipants').then(participants => {
          cy.fixture('user1').then(user1 => {
            cy.fixture('user2').then(user2 => {
              cy.intercept(
                {
                  method: 'GET',
                  pathname: '/api/frontend/events/1000/record/participants/',
                },
                {
                  body: merge(participants, {
                    results: [...participants.results, user1, user2],
                  }),
                },
              ).as('fetchParticipants')
            })
          })
        })

        cy.get('[class^=ImportParticipantsList_container]')
          .find('button')
          .contains('Přidat do seznamu')
          .click()

        // these data should match those provided in stylesheet (after transformation)
        // cypress/e2e/full-participants.xlsx
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

        cy.wait(['@createUser', '@createUser']).then(intercepts => {
          expect(
            intercepts
              .map(i => i.request.body)
              .sort((a, b) => (a.first_name > b.first_name ? 1 : -1)),
          ).to.deep.equal(expectations)
        })

        cy.wait('@updateEvent')
          .its('request.body.record.participants')
          // order is not certain, because of create-user intercepts' uncertain order
          .should('have.length', 6)
        /** TODO the following test is flaky - as if cypress
         * doesn't consistently intercept the two different
         * created users, but intercepts one twice
         * We turn it off for now
         */
        // .and('have.members', [
        //   '22222222-2d92-4645-9858-c89372669217',
        //   '00000000-1111-2222-3333-444444444444',
        //   'dddddddd-dddd-dddd-dddd-dddddddddddd',
        //   '11111111-1111-1111-1111-111111111111',
        //   '11111111-1111-1111-1111-1111111111ab',
        //   '22222222-2222-2222-2222-2222222222ab',
        // ])

        cy.wait('@fetchParticipants')

        // check that the users appear in the table
        cy.get('table[class^=ParticipantsStep_table] tbody tr').should(
          'have.length',
          6,
        )
      })

      it('should allow editing imported data', () => {
        // at the beginning, the table has 4 rows
        cy.get('table[class^=ParticipantsStep_table] tbody tr').should(
          'have.length',
          4,
        )

        cy.intercept(
          {
            method: 'GET',
            path: '/api/frontend/get_unknown_user/?birthday=1993-03-01&first_name=Jana&last_name=Nov%C3%A1kov%C3%A1',
          },
          { fixture: 'user1' },
        )

        cy.intercept(
          {
            method: 'GET',
            path: '/api/frontend/get_unknown_user/?birthday=1995-05-12&first_name=Dan&last_name=Nov%C3%A1k',
          },
          { statusCode: 404 },
        )

        cy.get('label:contains(Importovat z excelu)')
          .should('be.visible')
          .selectFile('cypress/e2e/full-participants.xlsx')

        cy.wait('@category_readHealthInsuranceCompanies').wait(100)

        // click one of the users
        cy.get(
          '[class^=ImportParticipantsList_container] table tbody tr[class^=ImportParticipantsList_userRow]',
        )
          .should('have.length', 2)
          .first()
          .click()

        // edit some of the user's fields
        cy.get('[class^=ImportParticipantsList_container] table tbody tr')
          .should('have.length', 3)
          .first()
          .next()
          .find('input[name="address.street"]')
          .should('have.value', 'Horní 50')
          .clear()
          .type('Rygol 123')
          // and confirm the form
          .parents('form')
          .find('button')
          .contains('Potvrdit')
          .click()

        // same for the second user
        cy.get(
          '[class^=ImportParticipantsList_container] table tbody tr[class^=ImportParticipantsList_userRow]',
        )
          .should('have.length', 2)
          .last()
          .click()

        cy.get('[class^=ImportParticipantsList_container] table tbody tr')
          .find('input[name="address.street"]')
          .should('have.value', 'Hlavní 5')
          .clear()
          .type('asdfasdf 123')
          .parents('form')
          .find('input[name=nickname]')
          .should('have.value', '')
          .type('Jablko')
          // and confirm the form
          .parents('form')
          .find('button')
          .contains('Potvrdit')
          .click()

        cy.intercept(
          { method: 'POST', pathname: '/api/frontend/users/', times: 1 },
          { fixture: 'user1' },
        ).as('createUser')

        cy.intercept(
          { method: 'PATCH', pathname: '/api/frontend/users/*/', times: 1 },
          { fixture: 'user2' },
        ).as('updateUser')

        cy.get('[class^=ImportParticipantsList_container]')
          .find('button')
          .contains('Přidat do seznamu')
          .click()

        // check that users get created/updated with the right data
        cy.wait('@createUser')
          .its('request.body')
          .should('deep.equal', {
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

        cy.wait('@updateUser')
          .its('request.body')
          .should('deep.equal', {
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

      it('[invalid data] should show invalid rows highlighted')
    })
  })
})
