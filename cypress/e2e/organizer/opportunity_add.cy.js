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

let url = "org/prilezitosti/vytvorit"

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

describe('Add opportunity', () =>

    it('empty', () =>
        console.log("Empty")
    ),

    it('can add new opportunity', () => {
        cy.visit(url)
        cy.contains("Spolupráce").click()
        cy.get('input[name="name"]').type("Příležitost spolupráce")
        cy.get('input[name="start"]').type("2022-01-01")
        cy.get('input[name="end"]').type("2025-12-31")
        cy.get('input[name="on_web_start"]').type("2023-12-31")
        cy.get('input[name="on_web_end"]').type("2023-12-31")

        cy.get('input[id="react-select-2-input"').focus().type("Brno").wait(2500).trigger('keydown', {
            key: 'Enter',
        });
        cy.get('p').each(($element, $index) => {
            if ($index <= 4) {
                cy.wrap($element).click({ force: true }).type("Text")
            }
        })

        // TODO: Add a photo and submit
    })
)

