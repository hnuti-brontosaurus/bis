describe('Edit user', () => {
  beforeEach(() => {
    cy.interceptCategories()
    cy.interceptLogin({ fixture: 'organizer' })
    cy.login('test@example.com', 'correcthorsebatterystaple')
  })

  context('myself', () => {
    it('should be able to save my preferred pronoun', () => {
      cy.intercept(
        { method: 'GET', pathname: '/api/frontend/users/1234/' },
        { fixture: 'organizer' },
      )
      cy.visit('/profil/1234/upravit')

      cy.get('form').should('contain', 'Oslovení')
      cy.get('[name=pronoun]')
        .should('exist')
        .should('have.value', 1)
        .select('2')

      cy.intercept(
        { method: 'PATCH', pathname: '/api/frontend/users/*/' },
        { statusCode: 200 },
      ).as('updateUser')
      cy.get('button').contains('Potvrdit').click()
      cy.wait('@updateUser')
        .its('request.body')
        .should('have.a.property', 'pronoun', 2)
    })

    it('should be able to save no pronoun', () => {
      cy.intercept(
        { method: 'GET', pathname: '/api/frontend/users/1234/' },
        { fixture: 'organizer' },
      )
      cy.visit('/profil/1234/upravit')

      cy.get('form').should('contain', 'Oslovení')
      cy.get('[name=pronoun]').should('exist').should('have.value', 1).select(0)

      cy.intercept(
        { method: 'PATCH', pathname: '/api/frontend/users/*/' },
        { statusCode: 200 },
      ).as('updateUser')
      cy.intercept(
        { method: 'GET', pathname: '/api/frontend/users/*/' },
        { fixture: 'organizer' },
      )
      cy.get('button').contains('Potvrdit').click()

      cy.wait('@updateUser')
        .its('request.body')
        .should('have.a.property', 'pronoun', null)
    })
  })

  context('other user', () => {
    it('[i have access] should not be able to save pronoun', () => {
      cy.intercept(
        { method: 'GET', pathname: '/api/frontend/users/1234/' },
        { fixture: 'chairman' },
      )
      cy.visit('/profil/1234/upravit')

      cy.get('form').should('not.contain', 'Oslovení')

      cy.get('[name=pronoun]').should('not.exist')
      cy.intercept(
        { method: 'PATCH', pathname: '/api/frontend/users/*/' },
        { statusCode: 200 },
      ).as('updateUser')
      cy.get('button').contains('Potvrdit').click()
      cy.wait('@updateUser')
        .its('request.body')
        .should('not.have.a.property', 'pronoun')
    })

    // not sure how to test this one
    it("[i don't have access] should show 403 error")
  })
})
