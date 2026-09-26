import { form2payload } from '../UserForm'

const baseFormData = {
  first_name: 'Don',
  last_name: 'Or',
  birthday: '2000-01-01',
  pronoun: 0,
  health_insurance_company: 0,
  email: 'don@example.com',
  phone: '',
  subscribed_to_newsletter: true,
  address: { street: 'Ulice 1', city: 'Praha', zip_code: '11000' },
  close_person: {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  },
  contact_address: { street: '', city: '', zip_code: '' },
}

describe('form2payload donor flags', () => {
  it('sends the donor flags when a checkbox is checked', () => {
    const payload = form2payload(
      {
        ...baseFormData,
        donor: { do_not_call: true, do_not_solicit: false },
      },
      true,
    )

    expect(payload.donor).toEqual({
      do_not_call: true,
      do_not_solicit: false,
    })
  })

  it('sends the donor object for an existing donor even with flags off', () => {
    const payload = form2payload(
      {
        ...baseFormData,
        donor: { do_not_call: false, do_not_solicit: false },
      },
      true,
      true,
    )

    expect(payload.donor).toEqual({
      do_not_call: false,
      do_not_solicit: false,
    })
  })

  it('does not create a donor when there is none and no flag is set', () => {
    const payload = form2payload(
      {
        ...baseFormData,
        donor: { do_not_call: false, do_not_solicit: false },
      },
      true,
      false,
    )

    expect(payload.donor).toBeNull()
  })

  it('keeps donor null when the form has no donor at all', () => {
    const payload = form2payload(baseFormData, true)

    expect(payload.donor).toBeNull()
  })
})
