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

describe('View events', () =>

    it('empty', () =>
        console.log("Empty")
    ),

    it('can view all my events', () => {
        cy.visit(url)
        // TODO: replace event names with events from testing DB
        let event_names = ["SMbyZHSDVs", "HuQjRmMkmZ"]
        // Validate all events and their order match.
        cy.get("tr").then((values) => {
            cy.wrap(values).should("have.length", event_names.length + 1) // +1 for header
            cy.wrap(values).each(($element, $index) => {
                // Skip header row
                if ($index == 0) {
                    ;
                } else {
                    cy.wrap($element).get('td').next().should('contain', event_names[$index - 1])
                }
            })
        })
    })

)


