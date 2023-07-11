/* The tests below is commented out because at the moment,
      we want to allow every organizer to create actions
      To make it work again (stop organizers without qualifications to create events), 
      just uncomment the file
      */

// describe('create event', () => {
//   // stub api endpoints before each request
//   beforeEach(() => {
//     cy.intercept(
//       { method: 'GET', pathname: '/api/categories/qualification_categories/' },
//       { fixture: 'qualificationCategories' },
//     )
//     cy.intercept('POST', '/api/auth/login/', { token: '1234567890abcdef' })
//     cy.intercept('GET', '/api/auth/whoami/', {
//       id: '0419781d-06ba-432b-8617-797ea14cf848',
//     })
//     cy.intercept(
//       { method: 'GET', path: /\/api\/frontend\/users\/[a-zA-Z0-9-]+\// },
//       { fixture: 'organizerWithoutQualifications' },
//     )
//   })

//   // sign in before each request
//   beforeEach(() => {
//     // https://xkcd.com/936/
//     cy.login('asdf@example.com', 'correcthorsebatterystaple')
//   })

//   it('shows a gray "NOVA AKCE" button that is disabled', () => {
//     cy.visit('/org/')
//     cy.location('pathname').should('equal', '/org/')

//     // check color of the button
//     cy.get('a[id=createEvent]')
//       .should('have.css', 'background-color')
//       .and('eq', 'rgb(244, 248, 250)')
//     cy.get('a[id=createEvent]')
//       .should('have.css', 'pointer-events')
//       .and('eq', 'none')
//   })

//   it("can't fill form and send data to create a new event", () => {
//     cy.visit('/org/akce/vytvorit')
//     cy.location('pathname').should('equal', '/org/akce/vytvorit')

//     // check that error message was shown
//     cy.contains('Nemáš dostatečná práva k TODO text organizátorskému přístupu')
//   })

//   it("can't clone an event", () => {
//     cy.visit('/org/akce/vytvorit?klonovat=1000')

//     // check that error message was shown
//     cy.contains('Nemáš dostatečná práva k TODO text organizátorskému přístupu')
//   })
// })
