import classNames from 'classnames'
import { ReactElement } from 'react'
import {
  FieldName,
  FieldValues,
  useFormContext,
  UseFormReturn,
} from 'react-hook-form'
import { getErrorMessage } from 'utils/helpers'
import styles from './FormInputError.module.scss'

export const FormInputError = <T extends FieldValues>({
  children,
  name,
  formMethods,
  ...props
}: {
  children: ReactElement
  name?: FieldName<T>
  formMethods?: UseFormReturn<T>
  isBlock?: boolean
  className?: string
}) => {
  const defaultMethods = useFormContext()

  const methods = formMethods ?? defaultMethods

  const errorMessage = getErrorMessage(
    methods.formState.errors,
    name ?? children.props.name,
  )

  return (
    <FormInputErrorSimple errorMessage={errorMessage} {...props}>
      {children}
    </FormInputErrorSimple>
  )
}

export const FormInputErrorSimple = ({
  children,
  isBlock,
  className,
  errorMessage,
}: {
  children: ReactElement
  isBlock?: boolean
  className?: string
  errorMessage?: string
}) => {
  return (
    <div
      className={classNames(
        isBlock ? styles.blockContainer : styles.container,
        className,
      )}
    >
      <div
        className={classNames(
          styles.inputWrapper,
          errorMessage && styles.isError,
        )}
      >
        {children}
      </div>
      <div className={styles.errorMessage}>{errorMessage ?? <>&nbsp;</>}</div>
    </div>
  )
}
