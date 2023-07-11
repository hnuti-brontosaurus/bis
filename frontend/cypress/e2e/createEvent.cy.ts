import type { Location } from '../../src/app/services/bisTypes'

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

// go to next step
const next = () =>
  cy
    .get('button[aria-label="Go to next step"]')
    .first()
    .should('be.visible')
    .click()

const submit = () =>
  cy.get('[type=submit]:contains(Uložit)').last().should('be.visible').click()

describe('create event', () => {
  // sign in before each request
  beforeEach(() => {
    cy.interceptCategories()
    cy.interceptLogin()
    // https://xkcd.com/936/
    cy.login('asdf@example.com', 'correcthorsebatterystaple')
  })

  // stub more api endpoints
  beforeEach(() => {
    cy.intercept('GET', '/api/web/administration_units/*', {
      results: [
        {
          id: 1,
          name: 'Aeiou',
          category: { id: 1, name: 'ZC', slug: 'zc' },
        },
      ],
    })
    cy.intercept('GET', '/api/frontend/locations/\\?*', { results: locations })
    cy.intercept('GET', '/api/frontend/search_users/?search=*', req => {
      req.reply({
        results: searchUsers
          .filter(user =>
            (
              user.display_name +
              user.first_name +
              user.last_name +
              user.nickname
            )
              .toLowerCase()
              .includes((req.query.search as string).toLowerCase()),
          )
          .slice(5),
      })
    })
    cy.intercept(
      { method: 'GET', pathname: '/api/frontend/users/' },
      { results: [] },
    )
  })

  it('can fill form and send data to create a new event', () => {
    cy.visit('/org/akce/vytvorit')
    cy.location('pathname').should('equal', '/org/akce/vytvorit')
    // first page
    cy.get('label[for=other]').should('be.visible').click()

    next()

    cy.get('input[name=name]').should('be.visible').type('Event Name III')
    cy.get('input[name=start]').should('be.visible').type('2123-01-15')
    cy.get('input[name=start_time]').should('be.visible').type('15:31')
    cy.get('input[name=end]').should('be.visible').type('2123-01-17')
    cy.get('[name=category]').should('be.visible').select(2)
    cy.get('[name=program]').should('be.visible').select('Akce příroda')
    cy.get('#react-select-3-input')
      .should('be.visible')
      .click()
      .type('{downArrow}{enter}')

    next()

    cy.get('input[name=intended_for]').should('be.visible').check('3')

    next()

    cy.get('#react-select-5-input')
      .should('be.visible')
      .click()
      .type('Location 3')
      .wait(2000)
      .type('{downArrow}{downArrow}{enter}')

    next()

    cy.get('[name="propagation.is_shown_on_web"]')
      .should('be.visible')
      .check('true')

    cy.get('[name=registrationMethod]').should('be.visible').check('none')

    next()

    cy.get('[name="propagation.cost"]').should('be.visible').type('10/100/1000')
    cy.get('[name="propagation.minimum_age"]').should('be.visible').type('12')
    cy.get('[name="propagation.maximum_age"]').should('be.visible').type('120')

    next()

    cy.get('#propagation\\.invitation_text_introduction')
      .should('be.visible')
      .type('intro')
    cy.get('#propagation\\.invitation_text_practical_information')
      .should('be.visible')
      .type('practical information')

    cy.get('[name=main_image\\.image]')
      .parent()
      .should('be.visible')
      .selectFile('cypress/e2e/image.png')
    cy.get('[name=images\\.0\\.image]')
      .parent()
      .should('be.visible')
      .selectFile('cypress/e2e/image.png')
    cy.get('[name=images\\.1\\.image]')
      .parent()
      .should('be.visible')
      .selectFile('cypress/e2e/image.png')
    cy.get('[name=images\\.2\\.image]')
      .parent()
      .should('be.visible')
      .selectFile('cypress/e2e/image.png')

    next()

    cy.get('#react-select-7-input')
      .should('be.visible')
      .click()
      .type('displayname2')
      .wait(2000)
      .type('{downArrow}{downArrow}{downArrow}{enter}')

    cy.get('[placeholder=DD]').should('be.visible').type('29')
    cy.get('[placeholder=MM]').should('be.visible').type('02')
    cy.get('[placeholder=RRRR]').should('be.visible').type('2000')
    cy.intercept(
      { method: 'GET', pathname: '/api/frontend/get_unknown_user/' },
      {
        id: '1345',
        first_name: 'FirstName',
        last_name: 'LastName',
        nickname: 'Nickname',
        _search_id: '27',
        display_name: 'Found User',
        birthday: '2000-01-01',
        qualifications: [],
        memberships: [{ year: 2123 }],
      },
    )
    cy.get('[type=submit]').contains('Pokračuj').should('be.visible').click()

    cy.get('input[name="propagation.contact_name"]').type('contact name')
    cy.get('input[name="propagation.contact_email"]').type('asdf@example.com')

    cy.intercept('POST', '/api/frontend/events/', req => {
      expect(req.body).to.have.property('name')
      // TODO add a bit more detailed test here
      req.reply({ id: 1 })
    }).as('createEvent')

    cy.intercept('POST', '/api/frontend/events/1/propagation/images/', {})
    cy.intercept('POST', '/api/frontend/events/1/questionnaire/questions/', {})

    submit()

    // test that event was saved
    cy.wait('@createEvent')

    // test that we got redirected to the event page
    cy.location('pathname').should('equal', '/org/akce/1')
  })

  it('shows validation errors', () => {
    // go to form
    cy.visit('/org/akce/vytvorit')
    cy.location('pathname').should('equal', '/org/akce/vytvorit')
    // submit form without filling data in
    submit()
    // still in the form
    cy.location('pathname').should('equal', '/org/akce/vytvorit')
    // check that error message was shown
    cy.contains('Opravte, prosím, chyby ve validaci')
  })

  it('can clone event', () => {
    cy.interceptFullEvent()
    cy.visit('/org/akce/vytvorit?klonovat=1000')

    // fill start and end date
    next()
    cy.get('input[name=start]').should('be.visible').type('2123-01-15')
    cy.get('input[name=end]').should('be.visible').type('2123-01-17')
    // and submit
    cy.intercept(
      { method: 'POST', pathname: '/api/frontend/events/' },
      { id: 1000 },
    ).as('createEvent')

    cy.intercept('POST', '/api/frontend/events/1000/propagation/images/', {})
    cy.intercept(
      'POST',
      '/api/frontend/events/1000/questionnaire/questions/',
      {},
    )

    submit()

    // test that event was submitted and proper data were sent to backend
    cy.wait('@createEvent')
      .its('request.body')
      .should('not.have.any.keys', 'is_canceled', 'is_closed', 'is_complete')
      .and('include', { record: null, finance: null })
  })

  it('shows api error message', () => {
    cy.interceptFullEvent()
    cy.visit('/org/akce/vytvorit?klonovat=1000')
    next()

    cy.get('input[name=start]').should('be.visible').type('2123-01-15')
    cy.get('input[name=end]').should('be.visible').type('2123-01-17')

    // submit and get error
    cy.intercept(
      { method: 'POST', pathname: '/api/frontend/events/' },
      {
        statusCode: 400,
        body: {
          name: ['Toto pole nesmí být prázdné.'],
          group: [
            'Chybný typ. Byl přijat typ dict místo hodnoty primárního klíče.',
          ],
          record: { total_hours_worked: ['Je vyžadováno celé číslo.'] },
        },
      },
    ).as('createEvent')

    cy.intercept('POST', '/api/frontend/events/1000/propagation/images/', {})

    submit()

    cy.wait('@createEvent').its('response.statusCode').should('equal', 400)

    cy.wait(5000)

    // for some buggy reason we need to fill the fields again
    cy.get('input[name=start]').should('be.visible').type('2123-01-15')
    cy.get('input[name=end]').should('be.visible').type('2123-01-17')

    cy.intercept(
      { method: 'POST', pathname: '/api/frontend/events/' },
      {
        statusCode: 400,
        body: [
          'Toto pole nesmí být prázdné.',
          'Chybný typ. Byl přijat typ dict místo hodnoty primárního klíče.',
          'Je vyžadováno celé číslo.',
        ],
      },
    ).as('createEvent2')

    submit()

    cy.wait('@createEvent2').its('response.statusCode').should('equal', 400)
  })

  describe('selecting standard registration form', () => {
    beforeEach(() => {
      // clone event and go to proper step
      cy.interceptFullEvent(27, 'simpleEvent')
      cy.visit('/org/akce/vytvorit?klonovat=27')
      next()

      cy.get('input[name=start]').should('be.visible').type('2123-01-15')
      cy.get('input[name=end]').should('be.visible').type('2123-01-17')

      fillPropagationFields()
      cy.get('button').contains('přihlášení').should('be.visible').click()
      cy.get('[name=registrationMethod]').check('standard')
    })

    // intercept POST responses
    beforeEach(() => {
      cy.intercept(
        { method: 'POST', pathname: '/api/frontend/events' },
        { id: 27 },
      ).as('createEvent')

      cy.intercept(
        {
          method: 'POST',
          pathname:
            '/api/frontend/events/27/registration/questionnaire/questions',
        },
        { times: 3 },
      ).as('createQuestion')

      cy.intercept(
        {
          method: 'POST',
          pathname: '/api/frontend/events/27/propagation/images/',
        },
        {},
      )
    })

    it('should save correct intro and after questionnaire text', () => {
      cy.get('[name="registration.questionnaire.introduction"]').type('foo')
      cy.get('[name="registration.questionnaire.after_submit_text"]').type(
        'bar',
      )
      submit()
      cy.wait('@createEvent')
        .its('request.body')
        .should('have.nested.deep.property', 'registration.questionnaire', {
          introduction: 'foo',
          after_submit_text: 'bar',
        })
    })

    it('should save correct empty intro and after questionnaire text', () => {
      submit()
      cy.wait('@createEvent')
        .its('request.body')
        .should('have.nested.deep.property', 'registration.questionnaire', {
          introduction: '',
          after_submit_text: '',
        })
    })

    it('should allow adding registration form questions and save it to api', () => {
      // add question and fill it
      cy.get('button').contains('Přidat otázku').click()
      cy.get('[name="questions.0.question"]').type('Otázka 1')
      cy.get('[name="questions.0.is_required"]').check()

      // add another question, type checkbox
      cy.get('button').contains('Přidat otázku').click()
      cy.get('[name="questions.1.question"]').type('Otázka 2')
      cy.get('[name="questions.1.data.type"]').select('checkbox')
      cy.get('button')
        .contains('Přidat možnost')
        .should('have.length', 1)
        .click()
      cy.get('[name^="questions.1.data.options"]').should('have.length', 2)

      cy.get('[name="questions.1.data.options.0.option"]').type('Option 1')
      cy.get('[name="questions.1.data.options.1.option"]').type('Option 2')

      // add another question, type radio
      cy.get('button').contains('Přidat otázku').click()
      cy.get('[name="questions.2.question"]').type('Otázka 3')
      cy.get('[name="questions.2.is_required"]').check()
      cy.get('[name="questions.2.data.type"]').select('radio')
      cy.get('button')
        .contains('Přidat možnost')
        .should('have.length', 2)
        .last()
        .click()
        .click()
      cy.get('[name="questions.2.data.options.0.option"]').type(
        'Radio option 1',
      )
      cy.get('[name="questions.2.data.options.1.option"]').type(
        'Radio option 2',
      )
      cy.get('[name="questions.2.data.options.2.option"]').type(
        'Radio option 3',
      )

      // submit and check that correct data are sent
      submit()

      cy.wait('@createEvent')

      cy.wait(['@createQuestion', '@createQuestion', '@createQuestion']).then(
        intercepts => {
          expect(intercepts.length).to.eql(3)
          const bodies = intercepts.map(i => i.request.body)
          expect(bodies).to.deep.include.members([
            {
              question: 'Otázka 1',
              data: { type: 'text' },
              is_required: true,
              order: 0,
            },
            {
              question: 'Otázka 2',
              data: {
                type: 'checkbox',
                options: [{ option: 'Option 1' }, { option: 'Option 2' }],
              },
              is_required: false,
              order: 1,
            },
            {
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
            },
          ])
        },
      )
    })
  })

  describe('selecting alternative registration form', () => {
    beforeEach(() => {
      // clone event and go to proper step
      cy.interceptFullEvent()
      cy.visit('/org/akce/vytvorit?klonovat=1000')
      next()

      cy.get('input[name=start]').should('be.visible').type('2123-01-15')
      cy.get('input[name=end]').should('be.visible').type('2123-01-17')

      cy.get('button:contains(přihlášení)').should('be.visible').click()
    })

    it('should allow selecting the option, filling link, and submitting', () => {
      cy.get('[name=registrationMethod]').should('be.visible').check('other')

      cy.get('[name="registration.alternative_registration_link"]')
        .should('be.visible')
        .type('https://example.com/some/link')

      cy.intercept(
        { method: 'POST', pathname: '/api/frontend/events' },
        { id: 1000 },
      ).as('createEvent')

      submit()

      cy.wait('@createEvent')
        .its('request.body')
        .should('deep.include', {
          registration: {
            is_registration_required: true,
            is_event_full: false,
            alternative_registration_link: 'https://example.com/some/link',
            questionnaire: null,
          },
        })
    })

    it('[link not filled] should fail with validation error', () => {
      cy.get('[name=registrationMethod]').should('be.visible').check('other')

      cy.get('[name="registration.alternative_registration_link"]')
        .should('be.visible')
        .click() // don't type anything...

      submit()

      cy.get('[class^=SystemMessage_header]')
        .should('be.visible')
        .contains('chyby ve validaci')
      cy.get('[class^=SystemMessage_detail]')
        .should('be.visible')
        .contains('Alternativní adresa pro přihlášení: Toto pole je povinné')
    })

    it('[link not valid url] should fail with validation error', () => {
      cy.get('[name=registrationMethod]').should('be.visible').check('other')

      cy.get('[name="registration.alternative_registration_link"]')
        .should('be.visible')
        .type('hello')

      submit()

      cy.get('[class^=SystemMessage_header]')
        .should('be.visible')
        .contains('chyby ve validaci')
      cy.get('[class^=SystemMessage_detail]')
        .should('be.visible')
        .contains('Alternativní adresa pro přihlášení: Zadejte platný odkaz')
    })

    it('should fill the form properly with default data', () => {
      // change initial data so there is alternative_registration_link filled
      // https://docs.cypress.io/api/commands/fixture#Modifying-fixture-data-before-using-it
      cy.fixture('event').then(event => {
        event.registration = {
          is_registration_required: true,
          is_event_full: false,
          alternative_registration_link: 'https://example.com/registration',
          questionnaire: null,
        }
        cy.intercept(
          { method: 'GET', pathname: '/api/frontend/events/1000/' },
          event,
        ).as('getUser')
      })
      cy.reload(true)

      cy.get('[name=registrationMethod]')
        .get('[value=other]')
        .should('be.visible')
        .should('be.checked')

      cy.get('[name="registration.alternative_registration_link"]')
        .should('be.visible')
        .should('have.value', 'https://example.com/registration')
    })
  })

  describe('organizer team and creator', () => {
    it('user should be pre-filled in team', () => {
      fillForm()
      cy.get('[name=other_organizers]')
        .parents('[class^=FormInputError_inputWrapper]')
        .contains('Nickname (FirstName LastName)')
    })

    context('user is organizer', () => {
      it('should show validation error when they are not part of team', () => {
        fillForm()
        // remove pre-filled organizer (self)
        cy.get('[name=other_organizers]')
          .parents('[class^=FormInputError_inputWrapper]')
          .get('[aria-label^=Remove][role=button]')
          .last()
          .click()

        submit()

        cy.get('[class^=SystemMessage_header]')
          .should('be.visible')
          .contains('chyby ve validaci')
        cy.get('[class^=SystemMessage_detail]')
          .should('be.visible')
          .contains('Musíš být v organizátorském týmu.')
      })

      it('should save event when user is part of organization team', () => {
        fillForm()
        // ok, user is pre-filled
        cy.get('[name=other_organizers]')
          .parents('[class^=FormInputError_inputWrapper]')
          .contains('Nickname (FirstName LastName)')

        // check that it's possible to submit
        cy.intercept(
          { method: 'POST', pathname: '/api/frontend/events' },
          { id: 1000 },
        ).as('createEvent')

        submit()

        cy.wait('@createEvent')
      })
    })

    context('user is administration unit', () => {
      beforeEach(() => {
        cy.visit('/logout')
        cy.interceptLogin({ fixture: 'chairman' })
        cy.login('a@bb.ccc', 'asdf')
      })

      it('should save even when they are not in team', () => {
        fillForm()

        // remove pre-filled organizer (self)
        cy.get('[name=other_organizers]')
          .parents('[class^=FormInputError_inputWrapper]')
          .get('[aria-label^=Remove][role=button]')
          .last()
          .click()

        // still succeed saving the event
        cy.intercept(
          { method: 'POST', pathname: '/api/frontend/events' },
          { id: 1000 },
        ).as('createEvent')

        submit()

        cy.wait('@createEvent')
      })
    })
  })

  describe('saving past event', () => {
    beforeEach(() => {
      // clone event
      cy.interceptFullEvent()
    })

    afterEach(() => {
      cy.restoreClock()
    })

    it('allow saving an event in the future', () => {
      cy.setClock('2023-01-05')
      cy.visit('/org/akce/vytvorit?klonovat=1000')
      next()

      cy.get('[name=start]').type('2023-02-10')
      cy.get('[name=end]').type('2023-02-12')

      cy.intercept(
        { method: 'POST', pathname: '/api/frontend/events' },
        { id: 1000 },
      ).as('createEvent')

      cy.intercept('POST', '/api/frontend/events/1000/propagation/images/', {})
      cy.intercept(
        'POST',
        '/api/frontend/events/1000/questionnaire/questions/',
        {},
      )

      submit()

      cy.wait('@createEvent')
    })

    it('after 03/01 forbid saving event from past year', () => {
      cy.setClock('2023-03-01')
      cy.visit('/org/akce/vytvorit?klonovat=1000')
      next()

      cy.get('[name=start]').type('2022-12-29')
      cy.get('[name=end]').type('2022-12-31')

      submit()

      cy.get('[class^=SystemMessage_header]')
        .should('be.visible')
        .contains('chyby ve validaci')
      cy.get('[class^=SystemMessage_detail]')
        .should('be.visible')
        .contains('Akci z minulého roku musíte uložit před koncem února')
    })

    it('before 03/01 allow saving event from past year', () => {
      cy.setClock('2023-02-28')
      cy.visit('/org/akce/vytvorit?klonovat=1000')
      next()

      cy.get('[name=start]').type('2022-12-29')
      cy.get('[name=end]').type('2022-12-31')

      cy.intercept(
        { method: 'POST', pathname: '/api/frontend/events' },
        { id: 1000 },
      ).as('createEvent')

      cy.intercept('POST', '/api/frontend/events/1000/propagation/images/', {})
      cy.intercept(
        'POST',
        '/api/frontend/events/1000/questionnaire/questions/',
        {},
      )

      submit()

      cy.wait('@createEvent')
      cy.get('@createEvent.all').should('have.length', 1)
    })

    it('before 03/01 forbid saving event from two years ago', () => {
      cy.setClock('2023-02-28')
      cy.visit('/org/akce/vytvorit?klonovat=1000')
      next()

      cy.get('[name=start]').type('2021-12-29')
      cy.get('[name=end]').type('2021-12-31')

      submit()

      cy.get('[class^=SystemMessage]')
        .should('contain', 'chyby ve validaci')
        .should('contain', 'Začátek akce:')
    })

    context('admin or office_worker', () => {
      ;['admin', 'office_worker'].forEach(role => {
        it(`[${role}] should be allowed to save event in deeper past`, () => {
          cy.visit('/logout')
          cy.interceptLogin({ fixture: role })
          cy.login('asdf@example.com', 'correcthorsebatterystaple')

          cy.setClock('2023-02-28')
          cy.visit('/org/akce/vytvorit?klonovat=1000')
          next()

          cy.get('[name=start]').type('2020-12-29')
          cy.get('[name=end]').type('2020-12-31')

          cy.intercept(
            { method: 'POST', pathname: '/api/frontend/events' },
            { id: 1000 },
          ).as('createEvent')

          cy.intercept(
            'POST',
            '/api/frontend/events/1000/propagation/images/',
            {},
          )
          cy.intercept(
            'POST',
            '/api/frontend/events/1000/questionnaire/questions/',
            {},
          )

          submit()

          cy.wait('@createEvent')
          cy.get('@createEvent.all').should('have.length', 1)
        })
      })
    })
  })

  describe('VIP propagation', () => {
    beforeEach(() => {
      fillForm()
      cy.get('button').contains('pro koho').should('be.visible').click()
      cy.get('input[name=intended_for]').check('5', { force: true })

      cy.intercept(
        { method: 'POST', pathname: '/api/frontend/events' },
        { id: 1000 },
      ).as('createEvent')
      cy.intercept('POST', '/api/frontend/events/1000/propagation/images/', {})
      cy.intercept(
        'POST',
        '/api/frontend/events/1000/questionnaire/questions/',
        {},
      )
    })

    it('[no VIP fields filled] should respond with vip_propagation null', () => {
      // type a bit but change my mind...
      cy.get('[name="vip_propagation.goals_of_event"]')
        .type('goals of event are goals')
        .clear()

      submit()

      cy.wait('@createEvent')
        .its('request.body')
        .should('have.property', 'vip_propagation', null)
    })

    it('[all vip fields filled] should respond with vip_propagation data', () => {
      cy.get('[name="vip_propagation.goals_of_event"]').type(
        'goals of event are goals',
      )
      cy.get('[name="vip_propagation.program"]').type(
        'program is rich and full of events',
      )
      cy.get('[name="vip_propagation.short_invitation_text"]').type(
        'you are cordially but shortly invited',
      )

      submit()

      cy.wait('@createEvent')
        .its('request.body.vip_propagation')
        .should('deep.equal', {
          goals_of_event: 'goals of event are goals',
          program: 'program is rich and full of events',
          short_invitation_text: 'you are cordially but shortly invited',
        })
    })

    it('[some vip fields filled] should show validation error (fill all or none)', () => {
      cy.get('[name="vip_propagation.goals_of_event"]').type(
        'goals of event are goals',
      )

      submit()

      cy.get('[class^=SystemMessage_header]')
        .should('be.visible')
        .contains('chyby ve validaci')
      cy.get('[class^=SystemMessage_detail]')
        .should('be.visible')
        .contains('Vyplňte všechna pole VIP propagace, nebo je nechte prázdná')
    })
  })
})

// open create-event page, pre-fill fields and move to "team" tab
const fillForm = () => {
  cy.visit('/org/akce/vytvorit')
  cy.location('pathname').should('equal', '/org/akce/vytvorit')
  // first page
  cy.get('label[for=other]').should('be.visible').click()

  next()

  cy.get('input[name=name]').should('be.visible').type('Event Name III')
  cy.get('input[name=start]').should('be.visible').type('2023-01-15')
  cy.get('input[name=start_time]').should('be.visible').type('15:31')
  cy.get('input[name=end]').should('be.visible').type('2023-01-17')
  cy.get('[name=category]').should('be.visible').select(2)
  cy.get('[name=program]').should('be.visible').select('Akce příroda')
  cy.get('#react-select-3-input')
    .should('be.visible')
    .click()
    .type('{downArrow}{enter}')

  next()

  cy.get('input[name=intended_for]').should('be.visible').check('3')

  next()

  cy.get('#react-select-5-input')
    .should('be.visible')
    .click()
    .type('Location 3')
    .wait(2000)
    .type('{downArrow}{downArrow}{enter}')

  next()

  cy.get('[name="propagation.is_shown_on_web"]')
    .should('be.visible')
    .check('false')

  next()

  cy.get('#react-select-7-input')
    .should('be.visible')
    .click()
    .type('displayname2')
    .wait(2000)
    .type('{downArrow}{downArrow}{downArrow}{enter}')

  cy.get('[placeholder=DD]').should('be.visible').type('29')
  cy.get('[placeholder=MM]').should('be.visible').type('02')
  cy.get('[placeholder=RRRR]').should('be.visible').type('2000')
  cy.intercept(
    { method: 'GET', pathname: '/api/frontend/get_unknown_user/' },
    {
      id: '1345',
      first_name: 'FirstName',
      last_name: 'LastName',
      nickname: 'Nickname',
      _search_id: '27',
      display_name: 'Found User',
      birthday: '2000-01-01',
      qualifications: [],
      memberships: [
        { year: 2020 },
        { year: 2021 },
        { year: 2022 },
        { year: 2023 },
        { year: 2123 },
      ],
    },
  )
  cy.get('[type=submit]').contains('Pokračuj').should('be.visible').click()

  // when we submit too fast, tests fail
  // somehow main_organizer needs time to appear in form data
  cy.wait(1000)
}

const fillPropagationFields = () => {
  cy.get('button').contains('přihlášení').click()
  cy.get('[name="propagation.is_shown_on_web"]').check('true')

  cy.get('button').contains('info pro účastníky').click()

  cy.get('input[name="propagation.cost"]').type('0')
  cy.get('input[name="propagation.minimum_age"]').type('0')
  cy.get('input[name="propagation.maximum_age"]').type('120')

  cy.get('button').contains('pozvánka').click()

  cy.get('[id="propagation.invitation_text_introduction"]').type('foo')
  cy.get('[id="propagation.invitation_text_practical_information"]').type('bar')

  cy.get('button').contains('organizátorský tým').click()

  cy.get('input[name="propagation.organizers"]').type(
    'nickname, name and otherName',
  )

  cy.get('input[name="propagation.contact_name"]').type('contact name')
  cy.get('input[name="propagation.contact_email"]').type('asdf@example.com')
}
