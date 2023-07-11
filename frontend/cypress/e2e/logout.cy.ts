describe('Sign out', () => {
  beforeEach(() => {
    cy.interceptLogin()
    cy.login('asdf@example.com', 'correcthorsebatterystaple')
  })

  it('should sign out when going to /logout', () => {
    // test that local storage is populated with auth data
    cy.getAllLocalStorage().should(
      'have.deep.nested.property',
      'http://localhost:3000.persist:auth',
    )

    cy.visit('/logout')
    cy.intercept({ pathname: '/api/auth/logout/' }, {})
    cy.location('pathname').should('equal', '/login')

    // test that local storage is cleared
    cy.getAllLocalStorage().should(
      'not.have.deep.nested.property',
      'http://localhost:3000.persist:auth',
    )
  })

  it('should sign out when going to /logout even when api fails', () => {
    // test that local storage is populated with auth data
    cy.getAllLocalStorage().should(
      'have.deep.nested.property',
      'http://localhost:3000.persist:auth',
    )

    cy.visit('/logout')
    cy.intercept({ pathname: '/api/auth/logout/' }, { statusCode: 500 })
    cy.location('pathname').should('equal', '/login')

    // test that local storage is cleared
    cy.getAllLocalStorage().should(
      'not.have.deep.nested.property',
      'http://localhost:3000.persist:auth',
    )
  })
})
