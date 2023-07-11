describe('update opportunity', () => {
  // sign in before each request
  beforeEach(() => {
    cy.intercept('POST', '/api/auth/login/', { token: '1234567890abcdef' })
    cy.intercept('GET', '/api/auth/whoami/', {
      id: '0419781d-06ba-432b-8617-797ea14cf848',
    })
    cy.intercept(
      { method: 'GET', path: /\/api\/frontend\/users\/[a-zA-Z0-9-]+\/$/ },
      { fixture: 'organizer' },
    )

    cy.login('asdf@example.com', 'correcthorsebatterystaple')
  })

  context("opportunity doesn't exist", () => {
    beforeEach(() => {
      // when api doesn't find the opportunity
      cy.intercept(
        '/api/frontend/users/0419781d-06ba-432b-8617-797ea14cf848/opportunities/1000/',
        {
          statusCode: 404,
        },
      )
    })

    it("should show 404 when opportunity doesn't exist", () => {
      cy.visit('/org/prilezitosti/1000/upravit')

      // it should show 404
      cy.contains('404')
      cy.contains('Nepodařilo se nám najít příležitost')
    })
  })

  context('opportunity exists', () => {
    beforeEach(() => {
      cy.intercept(
        {
          method: 'GET',
          pathname:
            '/api/frontend/users/0419781d-06ba-432b-8617-797ea14cf848/opportunities/1000/',
        },
        { fixture: 'opportunity' },
      )
      cy.intercept('/api/frontend/locations/100/', { fixture: 'location' })
      cy.intercept(
        { method: 'GET', pathname: '/api/categories/opportunity_categories/' },
        { fixture: 'opportunityCategories' },
      )
    })

    it('should pre-fill the form with the data of the current opportunity', () => {
      // visit the edit opportunity page
      cy.visit('/org/prilezitosti/1000/upravit')

      // check that the form contains the data
      cy.get('input[type=radio][name=category]#location_help')
        .should('not.be.visible')
        .should('be.checked')
      cy.get('input[name=name]')
        .should('be.visible')
        .should('have.value', 'asdf')
      cy.get('[name=start]')
        .should('be.visible')
        .should('have.value', '2022-12-29')
      cy.get('[name=end]')
        .should('be.visible')
        .should('have.value', '2022-12-31')

      // TODO check the other fields
    })

    it('should persist the data until canceled', () => {
      // visit edit opportunity page
      cy.visit('/org/prilezitosti/1000/upravit')
      // change some inputs
      cy.get('input[name=name]')
        .should('be.visible')
        .clear()
        .type('somethingdifferent')
      // wait for the changes to get persisted
      cy.wait(1000)
      // refresh page
      cy.reload(true)
      // see that the inputs are still changed
      cy.get('input[name=name]')
        .should('be.visible')
        .should('have.value', 'somethingdifferent')

      // TODO change some other inputs

      // reset the form
      cy.get('[type="reset"]:contains(Zrušit)').should('be.visible').click()
      // go to the page again
      cy.visit('/org/prilezitosti/1000/upravit')
      // fields should be default now
      cy.get('input[name=name]')
        .should('be.visible')
        .should('have.value', 'asdf')
    })

    it('should send correct request(s) to backend when saving', () => {
      // visit edit opportunity page
      cy.visit('/org/prilezitosti/1000/upravit')

      // edit some inputs
      cy.get('input[name=name]').should('be.visible').clear().type('New name')

      // submit
      cy.intercept(
        {
          method: 'PATCH',
          pathname:
            '/api/frontend/users/0419781d-06ba-432b-8617-797ea14cf848/opportunities/1000/',
        },
        { fixture: 'opportunity' },
      ).as('updateOpportunity')

      cy.get('[type=submit]:contains(Uložit)').should('be.visible').click()

      // check the data that got sent to backend
      cy.wait('@updateOpportunity')
        .its('request.body')
        .should('include', { name: 'New name', location: 100 })
    })
  })
})
