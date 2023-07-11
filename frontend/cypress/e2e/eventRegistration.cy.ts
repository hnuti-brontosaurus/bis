describe('Standard event registration form', () => {
  context('not signed in', () => {
    beforeEach(() => {
      cy.intercept(
        { method: 'GET', pathname: '/api/web/events/2000/' },
        { fixture: 'webEvent' },
      )
    })

    it('should show form with personal data and questions', () => {
      cy.visit(
        '/akce/2000/prihlasit?next=https%3A%2F%2Fexample.com%2Fasdf%2Fghjkl',
      )

      // fill personal data
      cy.get('[name=first_name]').type('GivenName')
      cy.get('[name=last_name]').type('FamilyName')
      cy.get('[name=birthday-day]').type('12')
      cy.get('[name=birthday-month]').type('05')
      cy.get('[name=birthday-year]').type('1995')
      cy.get('[name=phone]').type('601001002')
      cy.get('[name=email]').type('test@example.com')
      cy.get('[name=note]').type('note')

      // fill questionnaire
      cy.get('[name="answers.0.answer"]').type('answer first question')
      cy.get('[name="answers.1.answer"]').check('Option 2')
      cy.get('[name="answers.1.answer"]').check('Option 1')

      cy.get('[name="answers.2.answer"]').check('Option 3')
      cy.get('[name="answers.2.answer"]').check('Option 1')
      cy.get('[name="answers.3.answer"]').type('answer to last question')

      // intercept api call and submit
      cy.intercept(
        {
          method: 'POST',
          pathname: '/api/frontend/events/2000/registration/applications/',
        },
        { statusCode: 200 },
      ).as('createApplication')

      cy.get('button').contains('Odeslat').click()

      // check request body
      cy.wait('@createApplication')
        .its('request.body')
        .should('deep.equal', {
          answers: [
            {
              answer: 'answer first question',
              question: 4,
            },
            {
              answer: 'Option 1',
              question: 3,
            },
            {
              answer: 'Option 1, Option 3',
              question: 5,
            },
            {
              answer: 'answer to last question',
              question: 6,
            },
          ],
          close_person: null,
          first_name: 'GivenName',
          last_name: 'FamilyName',
          phone: '601001002',
          email: 'test@example.com',
          note: 'note',
          birthday: '1995-05-12',
          address: null,
          state: 'pending',
          is_child_application: false,
        })

      // check that we switched to final page
      cy.get('body').should('contain', 'Hotovo')
      cy.get('button').contains('Hotovo').click()

      // if we want to perform tests on other domain, we need to specify origin
      cy.origin('example.com', () => {
        cy.url().should('equal', 'https://example.com/asdf/ghjkl')
      })
    })

    it('should fill and submit correct data for a child', () => {
      cy.visit(
        '/akce/2000/prihlasit?next=https%3A%2F%2Fexample.com%2Fasdf%2Fghjkl',
      )

      cy.get('[name=is_child_application]').check()

      // fill parent data
      cy.get('[name="close_person.first_name"]').type('ParentGivenName')
      cy.get('[name="close_person.last_name"]').type('ParentFamilyName')
      cy.get('[name="close_person.phone"]').type('601001002')
      cy.get('[name="close_person.email"]').type('test@example.com')

      // fill personal data
      cy.get('[name=first_name]').type('GivenName')
      cy.get('[name=last_name]').type('FamilyName')
      cy.get('[name=birthday-day]').type('12')
      cy.get('[name=birthday-month]').type('05')
      cy.get('[name=birthday-year]').type('2015')
      cy.get('[name=note]').type('note')

      // fill questionnaire
      cy.get('[name="answers.0.answer"]').type('answer first question')
      cy.get('[name="answers.1.answer"]').check('Option 2')
      cy.get('[name="answers.1.answer"]').check('Option 1')

      cy.get('[name="answers.2.answer"]').check('Option 3')
      cy.get('[name="answers.2.answer"]').check('Option 1')
      cy.get('[name="answers.3.answer"]').type('answer to last question')

      // intercept api call and submit
      cy.intercept(
        {
          method: 'POST',
          pathname: '/api/frontend/events/2000/registration/applications/',
        },
        { statusCode: 200 },
      ).as('createApplication')

      cy.get('button').contains('Odeslat').click()

      // check request body
      cy.wait('@createApplication')
        .its('request.body')
        .should('deep.equal', {
          answers: [
            {
              answer: 'answer first question',
              question: 4,
            },
            {
              answer: 'Option 1',
              question: 3,
            },
            {
              answer: 'Option 1, Option 3',
              question: 5,
            },
            {
              answer: 'answer to last question',
              question: 6,
            },
          ],
          close_person: {
            first_name: 'ParentGivenName',
            last_name: 'ParentFamilyName',
            phone: '601001002',
            email: 'test@example.com',
          },
          first_name: 'GivenName',
          last_name: 'FamilyName',
          phone: '',
          email: '',
          note: 'note',
          birthday: '2015-05-12',
          address: null,
          state: 'pending',
          is_child_application: true,
        })

      // check that we switched to final page
      cy.get('body').should('contain', 'Hotovo')
      cy.get('button').contains('Hotovo').click()

      // if we want to perform tests on other domain, we need to specify origin
      cy.origin('example.com', () => {
        cy.url().should('equal', 'https://example.com/asdf/ghjkl')
      })
    })

    it('should forbid applying for past event', () => {
      cy.setClock('2123-03-09')
      cy.visit('/akce/2000/prihlasit')

      cy.contains('proběhla')
      cy.restoreClock()
    })

    it('should allow applying for event that ends today', () => {
      cy.setClock('2123-03-08')
      cy.visit('/akce/2000/prihlasit')

      cy.get('[name=first_name]')
      cy.restoreClock()
    })
  })
})
