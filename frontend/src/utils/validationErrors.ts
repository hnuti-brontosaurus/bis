import { get } from 'lodash'
import type { FieldErrorsImpl, FieldValues } from 'react-hook-form'
import { pickErrors } from './helpers'

export type ModelTranslations = Readonly<{
  [key: string]: string | Readonly<string[]> | ModelTranslations | undefined
  _name?: string
  _name_plural?: string
}>

export type GenericTranslations = { [key: string]: string }

/**
 * given field path, and translations, return the field's translation
 * when translation is not found, it falls back to the original path name
 */
export const getFieldName = (
  path: string,
  fieldNames: ModelTranslations,
  genericNames: GenericTranslations,
): string => {
  // try to get translation from model translations
  const model = get(fieldNames, path)
  // try to get translation from generic translations
  const generic = get(genericNames, path.split('.').pop() as string)
  // prefer model translation, then generic, and last raw path
  if (typeof model === 'string') return model
  else if (Array.isArray(model)) return model[0]
  else return generic ?? path
}

/**
 * Provide errors in react-hook-form format and translations of form field names
 * And you'll get a string ready to be displayed as error message
 */
export const validationErrors2Message = <FormShape extends FieldValues>(
  errors: FieldErrorsImpl<FormShape>,
  fieldNames: ModelTranslations = {},
  genericNames: GenericTranslations = {},
  limit: number = 10,
): string => {
  const namesWithMessages = getErrorPaths(
    pickErrors(errors) as NestedObject,
  ).map(path => [
    getFieldName(path, fieldNames, genericNames),
    get(errors, [path, 'message'].join('.')),
  ])

  let output = ''

  // show the error messages, but limit their amount
  namesWithMessages.slice(0, limit).forEach(([name, message]) => {
    output += `${name}: ${message}\n`
  })

  // when there are more than 0 omitted errors
  // show info that there is more
  const more = namesWithMessages.length - limit
  if (more > 0) {
    output += `a ${namesWithMessages.length - limit} další${
      more > 4 ? 'ch' : ''
    } chyb${more === 1 ? 'a' : more <= 4 ? 'y' : ''}…`
  }

  return output
}

type NestedObject =
  | {
      [key: string]: NestedObject | number | string
    }
  | (number | string)[]

export const getObjectPaths = <O extends NestedObject>(obj: O): string[] =>
  Object.entries(obj)
    .filter(([key]) => key !== 'ref')
    .map(([key, value]) => {
      if (typeof value === 'object')
        return getObjectPaths(value).map(path => `${key}.${path}`)
      else return key
    })
    .flat()

export const getErrorPaths = <O extends NestedObject>(obj: O): string[] =>
  getObjectPaths(obj)
    .map(a => {
      const split = a.split('.')
      const last = split.pop()
      if (last === 'message') return split.join('.')
      else return ''
    })
    .filter(a => Boolean(a))
