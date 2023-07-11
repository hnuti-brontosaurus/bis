import { FC } from 'react'
import styles from './ErrorBox.module.scss'

export type ObjectWithStrings = { [s: string]: string | ObjectWithStrings }

const arrayStringsFromObject = (obj: ObjectWithStrings) => {
  const arrayOfMessages: string[] = []

  const getToValues = (o: ObjectWithStrings) => {
    for (const key in o) {
      const currentElement = o[key]
      if (typeof currentElement !== 'string') {
        getToValues(currentElement)
      } else {
        arrayOfMessages.push(currentElement)
      }
    }
  }
  getToValues(obj)
  return arrayOfMessages
}

interface IErrorBox {
  error: ObjectWithStrings | undefined | null
}

export const ErrorBox: FC<IErrorBox> = ({ error }) => {
  if (!error) return null

  return (
    <div className={styles.infoBoxError}>
      {arrayStringsFromObject(error).map(error => (
        <div>{error}</div>
      ))}
    </div>
  )
}
