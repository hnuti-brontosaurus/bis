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

let url_create_event = "org/akce/vytvorit"
let url_clone_event = "org/akce/vsechny"

describe('Add event', () =>

    it('empty', () =>
        console.log("Empty")
    ),

    it('can add new event', () => {
        cy.visit(url_create_event)

        cy.create_one_day_event("2023-02-09", "2023-02-09")//.then(value => console.log(value))
    }),

    it('can add new event', () => {
        cy.visit(url_create_event)

        cy.create_weekend_event("2023-02-17", "2023-02-19")//.then(value => console.log(value))
    })
)

describe("Clone event", () =>
    it('can clone my event', () => {
        cy.visit(url_clone_event)
        // TODO: replace event name with event from testing DB
        let event_name = "SMbyZHSDVs"
        cy.get("td").contains(event_name).first().click()
        cy.contains("klonovat").click()

        cy.get("button").contains("základní info").click()
        cy.get('input[name="name"]').type(" (Naklonovaná)")
        cy.get('input[id="start"]').type("2025-01-01")
        cy.get('input[id="end"]').type("2025-01-03")

        cy.get('button[type="submit"]').first().click({ force: true })
    })
)


