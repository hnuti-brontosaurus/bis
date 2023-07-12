import { FetchBaseQueryError } from '@reduxjs/toolkit/query'
import { get } from 'lodash'
import {
  GenericTranslations,
  getFieldName,
  getObjectPaths,
  ModelTranslations,
} from './validationErrors'

export const apiErrors2Message = (
  error: FetchBaseQueryError,
  fieldNames: ModelTranslations = {},
  genericNames: GenericTranslations = {},
  // limit: number = Infinity,
): string => {
  let output = ''
  output += error.status

  // show root errors
  if (Array.isArray(error.data)) {
    output += '\n' + error.data.join('\n')
  }
  // or show nicely formatted errors
  else if (error.data && typeof error.data === 'object') {
    const namesWithMessages = getObjectPaths(error.data as {})
      .map(path => {
        // if last element is a digit, remove it
        if (/^\d+$/.test(path.split('.').pop() ?? '')) {
          path = path.split('.').slice(0, -1).join('.')
        }
        return path
      })
      .map(path => [
        getFieldName(path, fieldNames, genericNames),
        get(error.data, path),
      ])

    namesWithMessages.forEach(([name, errors]) => {
      output += `\n${name}: ${
        typeof errors === 'string'
          ? errors
          : Array.isArray(errors)
          ? errors.join(' ')
          : JSON.stringify(errors)
      }`
    })
  } else if (error.status === 'PARSING_ERROR' && error.originalStatus === 500) {
    output = '500\nDošlo k chybě na serveru. Zkus to znovu nebo nám dej vědět.'
  }
  // or JSON.stringify the response body
  else {
    output += `\n${JSON.stringify(error.data, null, 2)}`
  }

  return output
}
