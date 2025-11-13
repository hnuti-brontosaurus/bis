import type { Address, EventCategory } from 'app/services/bisTypes'
import dayjs from 'dayjs'
import { cloneDeep, mapValues } from 'lodash'
import get from 'lodash/get'
import isEmpty from 'lodash/isEmpty'
import padStart from 'lodash/padStart'
import {
  FieldError,
  FieldErrors,
  FieldErrorsImpl,
  FieldName,
  FieldValues,
  UseFormReturn,
} from 'react-hook-form'
import { Schema } from 'type-fest'
import { required } from './validationMessages'
import * as validationMessages from './validationMessages'

export function getIdBySlug<T, O extends { id: number; slug: T }>(
  objects: O[],
  slug: O['slug'],
): number {
  return objects.find(obj => obj.slug === slug)?.id ?? -1
}
export function getIdsBySlugs<T, O extends { id: number; slug: T }>(
  objects: O[],
  slugs: O['slug'][],
): number[] {
  return slugs.map(slug => getIdBySlug(objects, slug))
}

export const requireBoolean = {
  validate: (value: boolean | null | undefined) => {
    return value === true || value === false || required
  },
}

export const file2base64 = async (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => {
      resolve(addFilename(reader.result as string, file.name))
    }
    reader.onerror = e => reject(e)
  })

const addFilename = (url: string, filename: string) => {
  const [data, ...rest] = url.split(';')
  return [
    data,
    `filename=${getFilenameWithoutExtension(filename)}`,
    ...rest,
  ].join(';')
}

const getFilenameFromUrl = (url: string): string =>
  url.split('/').pop() as string

const getFilenameWithoutExtension = (filename: string): string =>
  filename.substring(0, filename.lastIndexOf('.')) || filename

/*
https://stackoverflow.com/a/20285053

fetch image and convert it to base64
*/
export const toDataURL = async (url: string): Promise<string> => {
  const response = await fetch(
    process.env.REACT_APP_CORS_PROXY
      ? process.env.REACT_APP_CORS_PROXY + url
      : url,
  )
  const blob = await response.blob()
  const dataURL = await new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })

  return addFilename(
    dataURL,
    getFilenameWithoutExtension(getFilenameFromUrl(url)),
  )
}

// event should be finished before March next year
const shouldBeFinishedUntil = (event: { end: string }): number => {
  const eventEnd = new Date(event.end)
  eventEnd.getFullYear()

  let finishUntil = new Date(0)
  finishUntil.setFullYear(eventEnd.getFullYear() + 1)
  finishUntil.setMonth(2) // this means March (months are zero-based)
  finishUntil.setDate(1)

  return finishUntil.getTime()
}

/**
 * Get oldest date that a saved event can start at
 * @returns date string in format YYYY-MM-DD
 */
export const getEventCannotBeOlderThan = (): string => {
  // events can be saved until 03/01 next year
  // if today is march
  const now = new Date()
  const isBeforeMarch = now.getMonth() < 2
  const allowedYear = isBeforeMarch ? now.getFullYear() - 1 : now.getFullYear()
  return `${allowedYear}-01-01`
}

export const EVENT_CATEGORY_VOLUNTEERING_SLUG: EventCategory['slug'] =
  'public__volunteering'

export const splitDateTime = (datetime: string): [string, string] => {
  const [date] = datetime.split('T')
  const d = new Date(datetime)
  const time = `${padStart(String(d.getHours()), 2, '0')}:${padStart(
    String(d.getMinutes()),
    2,
    '0',
  )}`
  return [date, time]
}

export const joinDateTime = (date: string, time: string = ''): string => {
  const [rawHours, rawMinutes] = time.split(':')
  const ddRegexp = /^\d\d$/
  const hours = ddRegexp.test(rawHours) ? rawHours : '00'
  const minutes = ddRegexp.test(rawMinutes) ? rawMinutes : '00'

  return `${date}T${hours}:${minutes}`
}

// A little function which prepares react-hook-forms errors for stringifying
// in particular, it removes circular references caused by error.ref
export const pickErrors = (errors: FieldErrorsImpl) => {
  if (errors && 'message' in errors && typeof errors.message === 'string') {
    delete errors.ref
  } else {
    for (const key in errors) {
      if (key in errors) {
        pickErrors(errors[key] as any)
      }
    }
  }
  return errors
}

/**
 * Given react-hook-form methods, returns boolean indicating whether the form has errors or not
 * @param react-hook-form methods returned by useForm
 * @returns boolean
 */
export const hasFormError = <T extends FieldValues>(
  methods: UseFormReturn<T>,
): boolean => !isEmpty(methods.formState.errors)

/**
 * Take array of strings and return string
 * element0, element1, element2, element3 a element4
 */
export const joinAnd = (values: string[]): string => {
  const formatter = new Intl.ListFormat('cs', {
    style: 'long',
    type: 'conjunction',
  })
  return formatter.format(values)
}

/**
 * Make nicely formatted date range
 * i.e. don't repeat year and month and day when it's the same
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat/formatRange
 */
export const formatDateRange = (startDate: string, endDate: string) => {
  try {
    const dateTimeFormat = new Intl.DateTimeFormat('cs', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
    return dateTimeFormat.formatRange(new Date(startDate), new Date(endDate))
  } catch {
    // version for older browsers
    if (startDate === endDate) return formatDateTime(startDate)
    else return formatDateTime(startDate) + ' - ' + formatDateTime(endDate)
  }
}

/**
 * provide date as YYYY-MM-DD and time (optionally) as hh:mm
 * and this function returns nicely formated datetime (or date (if time is omitted))
 * locale is czech, feel free to make the function more generic if you need
 */
export const formatDateTime = (date: string, time?: string): string => {
  if (time) {
    const dateTimeFormat = new Intl.DateTimeFormat('cs', {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
    })
    const datetime = joinDateTime(date, time)
    return dateTimeFormat.format(new Date(datetime))
  } else {
    const dateTimeFormat = new Intl.DateTimeFormat('cs', {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
    })
    return dateTimeFormat.format(new Date(date))
  }
}

/**
 * Formats date to datestring format used in forms and on backend.
 */
export const toDateString = (date: Date): string => {
  return dayjs(date).format('YYYY-MM-DD')
}

/**
 * Formats an address as a string.
 *
 * The string format is "Za Humny, 63405 Horní Dolní".
 */
export const formatAddress = (address: Address): string => {
  return `${address.street}, ${address.zip_code} ${address.city}`
}

/**
 * This is a helper function for lodash mergeWith
 * lodash.merge doesn't overwrite arrays, but merges them.
 * When we want to overwrite arrays, we may use mergeWith as follows:
 * lodash.mergeWith(obj1, obj2, obj3, withOverwriteArray)
 *
 * https://stackoverflow.com/a/66247134
 */
export const withOverwriteArray = (a: any, b: any) =>
  Array.isArray(b) ? cloneDeep(b) : undefined

/**
 * remove html tags from html document
 */
export const stripHtml = (html: string): string => {
  let doc = new DOMParser().parseFromString(html, 'text/html')
  return doc.body.textContent || ''
}

/* This sorts lowest order first, and highest or missing order last */
export const sortOrder = <T extends { order?: number }>(a: T, b: T) => {
  const aOrder = a.order ?? Infinity
  const bOrder = b.order ?? Infinity
  return aOrder - bOrder
}

/**
 * Input unnormalized object and config that shows how raw object keys map on final object key
 * Output object with normalized keys and the same values as the other one
 */
export const array2object = <T extends { [key: string]: unknown }>(
  arr: unknown[],
  shape: Schema<T, number>,
): T =>
  mapValues(shape, value =>
    typeof value === 'number' ? arr[value] : array2object(arr, value),
  ) as T

/**
 * Transform string to lowercase without diacritics, for more graceful comparison
 * and when it's not string, return the original value
 */
export const normalizeString = (input: string): string => {
  if (typeof input !== 'string') return input
  return (
    input
      .toLowerCase()
      // remove diacritics https://stackoverflow.com/a/37511463/4551707
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
  )
}

/**
 * Given form errors and field name, return error message
 * It's meant to be used with react-hook-form
 */
export const getErrorMessage = <T extends FieldValues>(
  errors: FieldErrors<T>,
  name: FieldName<T>,
) => (get(errors, name) as FieldError | undefined)?.message

/**
 * Validates whether a given string is a properly formatted URL.
 */
export const validateUrl = (value?: string) => {
  if (!value) {
    return true // Allow empty string as valid input since the URL can be optional
  }
  try {
    new URL(value as string)
    return true
  } catch (e) {
    return validationMessages.url
  }
}
