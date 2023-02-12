// ***********************************************************
// This example support/e2e.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import "cypress-localstorage-commands";
import "../../support/commands"

let url = "org/akce/vsechny"

before(() => {

    cy.clearAllLocalStorage()
    cy.setLocalStorage("persist:auth", JSON.stringify({
        "token": "\"token\"",
    }))

    cy.saveLocalStorage("user")
})


beforeEach(() => {
    cy.restoreLocalStorage("user")
})

describe('Edit events', () =>

    it('empty', () =>
        console.log("Empty")
    ),

    it('can edit my event', () => {
        cy.visit(url)
        // TODO: replace event name with event from testing DB
        let event_name = "SMbyZHSDVs"
        cy.get("td").contains(event_name).click()
        cy.contains("upravit").click()
        cy.get('button[type="submit"]').first().click({ force: true })
    }),

)


