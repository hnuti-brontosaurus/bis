import {
  AddressPayload,
  HealthInsuranceCompany,
  User,
  UserPayload,
} from 'app/services/bisTypes'
import { data2form, form2payload } from 'components/UserForm/UserForm'
import dayjs from 'dayjs'
import { merge, pick } from 'lodash'
import { normalizeString } from 'utils/helpers'
import { UserImport } from '../ImportParticipants'

/**
 * Convert raw imported excel data into usable data
 *
 * In particular, parse addresses and other data,
 * convert health_insurance_company from its name to id,
 * merge with the fetched user
 * ...
 */
export const import2payload = (
  data: UserImport,
  {
    healthInsuranceCompanies,
    loaded,
  }: {
    healthInsuranceCompanies: HealthInsuranceCompany[]
    loaded: User | undefined
  },
): UserPayload & { id?: string } => {
  const originalFields = pick(
    data,
    'first_name',
    'last_name',
    'nickname',
    'birth_name',
    'health_issues',
    'email',
  )

  const defaultFields = {
    birth_name: '',
    nickname: '',
    health_issues: '',
    pronoun: null,
    subscribed_to_newsletter: true,
    donor: null,
    offers: null,
    eyca_card: null,
    // default imported fields
    first_name: '',
    last_name: '',
    email: null,
    phone: '',
    close_person: null,
    address: null,
    contact_address: null,
    health_insurance_company: null,
  }

  const phone = String(data.phone ?? '')

  const close_person = data.close_person?.first_name
    ? merge({}, data.close_person, {
        phone: String(data.close_person?.phone),
      })
    : null

  const dayjsBirthday = dayjs(data.birthday, [
    'D.M.YYYY',
    'YYYY-M-D',
    'YYYY-MM-DD',
    'M/D/YYYY',
  ])

  const birthday = dayjsBirthday.isValid()
    ? dayjsBirthday.format('YYYY-MM-DD')
    : null

  const address = data.address?.trim?.() ? parseAddress(data.address) : null
  const contact_address = data.contact_address?.trim?.()
    ? parseAddress(data.contact_address)
    : null

  const health_insurance_company = data.health_insurance_company
    ? healthInsuranceCompanies.find(
        company =>
          normalizeString(company.slug) ===
          normalizeString(data.health_insurance_company),
      )?.id ?? null
    : null

  const preparedFields = {
    ...originalFields,
    birthday,
    phone,
    close_person,
    address,
    contact_address,
    health_insurance_company,
  } as const

  const importedFields = Object.fromEntries(
    Object.entries(preparedFields).filter(([, value]) => Boolean(value)),
  ) as Partial<User>

  return merge(
    defaultFields,
    loaded && form2payload(data2form(loaded)),
    loaded?.id && { id: loaded.id },
    importedFields,
  )
}

/**
 * Parse address from string to address object
 *
 * It has to be in format
 * Street Number, Zip Code City
 * For example
 * Na Návsi 1, 76323 Horní Lhota
 * Vinohradská 1778/51a, 120 00 Praha 2
 *
 * Or in format
 * Street Number, City, Zip Code
 * Street Number, Zip Code, City
 */
const zipCodeRegex = /^((\d[-\s]?){2,5})$/
const zipAndCityRegex = /^((\d[-\s]?){2,4}\d)\s*(.+)$/
// const addressRegex = /^(.+),\s*(\d{3}\s?\d{2})\s*(.+)$/
const parseAddress = (input: string): AddressPayload => {
  const parts = input.split(/[,;]\s*/g)

  // street will always be the first
  const street = parts[0] ?? ''
  let zip_code = ''
  let city = ''

  // let's find if there is a zip code part
  // like this, it will be 0 when not found
  const zipCodeIndex =
    parts.slice(1).findIndex(part => zipCodeRegex.test(part)) + 1

  if (zipCodeIndex > 0) {
    zip_code = parts[zipCodeIndex]
  }

  // and if yes, we'll assume the other part is city
  const cityIndex = zipCodeIndex === 1 ? 2 : 1
  city = parts[cityIndex] ?? ''

  // otherwise, we try to parse zip code and city
  if (zipCodeIndex === 0) {
    const matches = zipAndCityRegex.exec(parts[1])
    if (matches) {
      zip_code = matches[1]
      city = matches[3]
    }
  }

  return { street, city, zip_code }
}
