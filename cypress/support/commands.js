// ***********************************************
// This example commands.js shows you how to
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

import { create_minimum_event_object } from "./utilities";

function fill_event_form(event_object, submit = true) {
    cy.get("button").contains("druh akce").click()
    cy.contains(event_object.kind).click()
    /// Basic info
    cy.get("button").contains("základní info").click()
    cy.get('input[name="name"').type(event_object.name)
    cy.get('input[id="start"').type(event_object.start_date)
    cy.get('input[id="end"').type(event_object.end_date)
    cy.get('input[name="number_of_sub_events"').clear().type(event_object.count)
    // Verejna - Dobrovolnicka
    cy.get('select[name="category"]').select("4")
    // Akce pamatky
    cy.get('select[name="program"]').select("2")
    // ZC - prvni v poradi
    // Would be better if frontend would put stable ID on the input element
    cy.contains("Select...").parent().find('input').click({ force: true }).trigger('keydown', {
        key: 'Enter',
    });

    /// Pro koho
    cy.get("button").contains("pro koho").click()
    if (event_object.for_first_time_participant) {
        cy.get('input[id="for_first_time_participant"]').click({ force: true })
        // NotImplemented
    } else {
        cy.get('input[id="for_all"]').click({ force: true })

    }
    /// Location
    cy.get("button").contains("místo konání").click()
    if (event_object.location == "online") {
        cy.get('input[name="online"]').click()
    } else {
        cy.contains("Název").parent().find('input').click({ force: true }).type("Brno").wait(1000).trigger('keydown', {
            key: 'Enter',
        });
    }
    /// Prihlaseni
    cy.get("button").contains("přihlášení").click()
    if (event_object.show_on_web) {
        // Not Implemented
        cy.get('input[type="radio"][id="Ano"]').click({ force: true })
        //// Displays only when shown on web
        /// Info pro ucastniky
        cy.get("button").contains("info pro účastníky").click()
        /// Pozvanka
        cy.get("button").contains("pozvánka").click()
    } else {
        cy.get('input[type="radio"][id="Ne"]').click({ force: true })
    }
    /// Organizers
    cy.get("button").contains("organizátorský tým").click()
    cy.contains("Select...").parent().find('input').click({ force: true }).type("Milan Another").wait(5000).trigger('keydown', {
        key: 'Enter',
    });

    if (submit) {
        cy.get('button[type="submit"]').first().click({ force: true })
        cy.url().should('match', /\d+$/)
    }
}

function create_one_day_event(start_date, end_date, count = 1, name = null) {
    let event_object = create_minimum_event_object("ONE_DAY", start_date, end_date, count, name)
    fill_event_form(event_object)
    cy.wrap(event_object)
}

function create_weekend_event(start_date, end_date, count = 1, name = null) {
    let event_object = create_minimum_event_object("WEEKEND", start_date, end_date, count, name)
    fill_event_form(event_object)
    cy.wrap(event_object)
}

function login(email, password) {
    // cy.session([email, password], () => {
    //     cy.visit('/login')
    //     cy.get('input[name="email"').type(email)
    //     cy.get('input[name="password"').type(password)
    //     cy.get('button[type="submit"').click()

    //     cy.wait(5000)
    //     // cy.visit('/')
    //     // cy.url().should("not.contain.text", 'login')

    // })
    cy.session([email, password], () => {
        cy.request({
            method: 'POST',
            url: 'api/auth/login/',
            body: {
                email: email,
                password: password,

            }
        })

            .then((resp) => {
                console.log(resp)
                console.log(resp.body)
                console.log(resp.body.token)
            })
    })
}

Cypress.Commands.add('login', login)
Cypress.Commands.add('create_one_day_event', create_one_day_event)
Cypress.Commands.add('create_weekend_event', create_weekend_event)


