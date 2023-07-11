import * as translations from 'config/static/translations'
import { merge } from 'lodash'
export * from 'config/static/translations'

export const event = merge(
  {},
  translations.event,
  {
    propagation: translations.eventPropagation,
    registration: translations.eventRegistration,
    record: translations.eventRecord,
    finance: translations.eventFinance,
    images: translations.eventPropagationImage,
    questions: translations.question,
    vip_propagation: translations.vIPEventPropagation,
    registrationMethod: 'Způsob přihlášení',
  },
  {
    registration: { questionnaire: translations.questionnaire },
    record: { participantInputType: 'Způsob zadání účastníků' },
  },
  { 'main_image.image': 'Hlavní foto' },
  {
    questions: {
      data: {
        _name: translations.question.data,
        type: 'Typ',
        options: { _name: 'Možnosti', option: 'Možnost' },
      },
    },
  },
)

export const user = merge({}, translations.user, {
  qualifications: translations.qualification,
  memberships: translations.membership,
  address: translations.userAddress,
  contact_address: translations.userContactAddress,
  all_emails: 'Všechny e-maily',
})
