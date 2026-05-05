describe('Sign out', () => {
  // redux-persist keys localStorage by origin; derive from the configured
  // baseUrl so the spec works against both the dev stack (localhost:3000)
  // and the isolated test stack (localhost:8090).
  const persistKey = `${Cypress.config('baseUrl')}.persist:auth`

  beforeEach(() => {
    cy.interceptLogin()
    cy.login('asdf@example.com', 'correcthorsebatterystaple')
  })

  it('should sign out when going to /logout', () => {
    // test that local storage is populated with auth data
    cy.getAllLocalStorage().should('have.deep.nested.property', persistKey)

    cy.visit('/logout')
    cy.intercept({ pathname: '/api/auth/logout/' }, {})
    cy.location('pathname').should('equal', '/login')

    // test that local storage is cleared
    cy.getAllLocalStorage().should('not.have.deep.nested.property', persistKey)
  })

  it('should sign out when going to /logout even when api fails', () => {
    // test that local storage is populated with auth data
    cy.getAllLocalStorage().should('have.deep.nested.property', persistKey)

    cy.visit('/logout')
    cy.intercept({ pathname: '/api/auth/logout/' }, { statusCode: 500 })
    cy.location('pathname').should('equal', '/login')

    // test that local storage is cleared
    cy.getAllLocalStorage().should('not.have.deep.nested.property', persistKey)
  })
})
