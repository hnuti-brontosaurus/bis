/// <reference types="cypress" />

import { RouteHandler } from 'cypress/types/net-stubbing'

// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//
// declare global {
//   namespace Cypress {
//     interface Chainable {
//       login(email: string, password: string): Chainable<void>
//       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
//     }
//   }
// }

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to select DOM element by data-cy attribute.
       * @example cy.dataCy('greeting')
       */
      login(
        email: string,
        password: string,
        redirect?: string,
      ): Chainable<Element>
      interceptFullEvent(id?: number, fixture?: string): Chainable<Element>
      interceptLogin(userResponse?: RouteHandler): Chainable<Element>
      interceptCategories(): Chainable<Element>
      setClock(date: string): Chainable<Element>
      restoreClock(): Chainable<Element>
    }
  }
}

Cypress.Commands.add(
  'login',
  (email: string, password: string, redirect = '/') => {
    cy.visit(redirect)
    // redirect to /login page
    cy.location('pathname').should('equal', '/login')
    // fill in email and password
    cy.get('input[name=email]').should('be.visible').type(email)
    cy.get('input[name=password]')
      .should('be.visible')
      .type(password, { log: false })
    cy.get('[type=submit]').should('be.visible').click()
    // api request is sent
    if (redirect === '/') {
      cy.location('pathname').should('not.contain', 'login')
    } else {
      cy.location('pathname').should('equal', redirect)
    }
  },
)

// providing id is not implemented
Cypress.Commands.add('interceptFullEvent', (id = 1000, fixture = 'event') => {
  cy.intercept(
    { method: 'GET', pathname: `/api/frontend/events/${id}/` },
    { fixture },
  )
  cy.intercept(
    {
      method: 'GET',
      pathname: `/api/frontend/events/${id}/propagation/images/`,
    },
    { fixture: 'eventPropagationImages' },
  )
  cy.intercept(
    {
      method: 'GET',
      pathname: `/api/frontend/events/${id}/registration/questionnaire/questions/`,
    },
    { results: [] },
  )
  cy.intercept(
    { method: 'GET', pathname: '/api/frontend/locations/100/' },
    { fixture: 'location' },
  )
  cy.intercept(
    {
      method: 'GET',
      pathname: /\/api\/frontend\/users\/[a-z0-9-]+\//,
    },
    { fixture: 'organizer' },
  )
  cy.intercept(
    { method: 'GET', pathname: '/api/frontend/users/' },
    { results: [] },
  )
})

Cypress.Commands.add('interceptLogin', (userResponse?: RouteHandler) => {
  cy.intercept('POST', '/api/auth/login/', { token: '1234567890abcdef' })
  cy.intercept('GET', '/api/auth/whoami/', {
    id: '0419781d-06ba-432b-8617-797ea14cf848',
  })
  cy.intercept(
    {
      method: 'GET',
      pathname: '/api/frontend/users/0419781d-06ba-432b-8617-797ea14cf848/',
    },
    userResponse ?? { fixture: 'organizer' },
  )
})

Cypress.Commands.add('interceptCategories', () => {
  cy.intercept(
    { method: 'GET', pathname: '/api/categories/qualification_categories/' },
    { fixture: 'qualificationCategories' },
  )
  cy.intercept(
    { method: 'GET', pathname: '/api/categories/health_insurance_companies/' },
    { fixture: 'healthInsuranceCompanies' },
  ).as('category_readHealthInsuranceCompanies')
  cy.intercept(
    { method: 'GET', pathname: '/api/categories/pronoun_categories/' },
    { fixture: 'pronouns' },
  )
  cy.intercept(
    { method: 'GET', pathname: '/api/categories/event_categories/' },
    { fixture: 'eventCategories' },
  )
  cy.intercept(
    { method: 'GET', pathname: '/api/categories/event_group_categories/' },
    { fixture: 'eventGroupCategories' },
  )
  cy.intercept(
    { method: 'GET', pathname: '/api/categories/event_program_categories/' },
    { fixture: 'eventProgramCategories' },
  )
  cy.intercept(
    {
      method: 'GET',
      pathname: '/api/categories/event_intended_for_categories/',
    },
    { fixture: 'eventIntendedForCategories' },
  )
  cy.intercept(
    { method: 'GET', pathname: '/api/categories/diet_categories/' },
    { fixture: 'dietCategories' },
  )
})

/**
 * Set a specific date
 */
Cypress.Commands.add('setClock', (date: string) => {
  cy.clock().then(clock => {
    clock.restore()
    cy.clock(new Date(date), ['Date'])
  })
})

/**
 * Restore clock
 * To be used after our custom cy.setClock
 */
Cypress.Commands.add('restoreClock', () => {
  cy.clock().then(clock => {
    clock.restore()
  })
})

export {}
