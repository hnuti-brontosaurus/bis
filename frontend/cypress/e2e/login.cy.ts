/// <reference types="Cypress" />
import { mergeWith } from 'lodash'
import type { User } from '../../src/app/services/bisTypes'
import { withOverwriteArray } from '../../src/utils/helpers'

const organizer: User = {
  id: '0419781d-06ba-432b-8617-797ea14cf848',
  roles: [
    {
      id: 1,
      name: 'asdf',
      slug: 'organizer',
    },
  ],
  qualifications: [
    {
      category: {
        id: 6,
        name: 'Vedoucí Brďo',
        slug: 'kids_leader',
        parents: [5],
      },
      valid_since: '01-01-2001',
      valid_till: '01-01-2400',
      approved_by: { first_name: 'fghj', last_name: 'hjkl' },
    },
  ],
  first_name: 'FirstName',
  last_name: 'LastName',
} as User

const user: User = mergeWith({}, organizer, { roles: [] }, withOverwriteArray)

describe('login', () => {
  beforeEach(() => {
    // cy.intercept(
    //   { method: 'GET', pathname: '/api/categories/qualification_categories/' },
    //   { fixture: 'qualificationCategories' },
    // )
    cy.intercept('POST', '/api/auth/login/', { token: '1234567890abcdef' })
    cy.intercept('GET', '/api/auth/whoami/', {
      id: '0419781d-06ba-432b-8617-797ea14cf848',
    })
  })

  it('can sign in as organizer', () => {
    cy.intercept('GET', '/api/frontend/users/*', organizer)
    // go to the app
    cy.visit('/')
    // redirect to /login page
    cy.location('pathname').should('equal', '/login')
    // fill in email and password
    cy.get('input[name=email]').should('be.visible').type('asdf@example.com')
    cy.get('input[name=password]')
      .should('be.visible')
      .type('correcthorsebatterystaples')
    cy.get('[type=submit]').should('be.visible').click()
    // api request is sent
    // app redirects to home
    cy.location('pathname').should('equal', '/')
    cy.contains('Organizátor')
    cy.contains('Po akci')
  })

  it('can sign in as user', () => {
    cy.intercept('GET', '/api/frontend/users/*', user)
    // go to the app
    cy.visit('/')
    // redirect to /login page
    cy.location('pathname').should('equal', '/login')
    // fill in email and password
    cy.get('input[name=email]').should('be.visible').type('asdf@example.com')
    cy.get('input[name=password]')
      .should('be.visible')
      .type('correcthorsebatterystaples')
    cy.get('[type=submit]').should('be.visible').click()
    // api request is sent
    // app redirects to home
    cy.location('pathname').should('equal', '/')
    cy.contains('Uživatel')
    cy.contains('Dárcovství')
  })
})
