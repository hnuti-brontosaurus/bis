import classNames from 'classnames'
import { Help, Web } from 'components'
import { HTMLAttributes, HTMLProps, ReactNode } from 'react'
import styles from './FormLayout.module.scss'

interface HeaderProps {
  children: ReactNode
  required?: boolean
  help?: ReactNode
  onWeb?: boolean
  className?: string
}

export const FormHeader = ({
  children,
  required,
  help,
  onWeb,
  numbered,
  className,
}: HeaderProps & {
  numbered?: boolean
}) => {
  return (
    <header
      className={classNames(numbered && styles.numberedHeader, className)}
    >
      {help && <Help>{help}</Help>}{' '}
      <span className={classNames(required && styles.required)}>
        {children}
      </span>{' '}
      {onWeb && <Web />}
    </header>
  )
}

export const FormNumberedHeader = (props: HeaderProps) => {
  return <FormHeader {...props} numbered />
}

export const FormSubheader = (props: HeaderProps) => {
  return <FormHeader {...props} />
}

/**
 * This component wraps sections in form
 * Practically it renders as a gray border around the particular sections
 */
export const FormSectionGroup = ({
  children,
  startIndex,
  className,
}: {
  children: ReactNode
  startIndex?: number
  className?: string
}) => {
  return (
    <fieldset
      style={{ counterReset: `section ${(startIndex ?? 1) - 1}` }}
      className={classNames(className, styles.sectionGroup)}
    >
      {children}
    </fieldset>
  )
}

/**
 * This is a component that wraps a form section
 * It has a numbered header
 *
 * Numbers withing FormSectionGroup get assinged automatically
 * but FormSectionGroup needs to specify at which index it should start
 * (TODO The manual indexing of FormSectionGroup is because of technical limitations. If you can think of better way, refactor! <3)
 */
export const FormSection = ({
  children,
  header,
  help,
  required,
  onWeb,
}: {
  children: ReactNode
  header: ReactNode
  help?: ReactNode
  required?: boolean
  onWeb?: boolean
}) => {
  return (
    <div className={styles.section}>
      <FormNumberedHeader required={required} help={help} onWeb={onWeb}>
        {header}
      </FormNumberedHeader>
      {children}
    </div>
  )
}

export const FormSubsection = ({
  children,
  header,
  help,
  required,
  onWeb,
  className,
  headerClassName,
}: {
  children: ReactNode
  header: ReactNode
  help?: ReactNode
  required?: boolean
  onWeb?: boolean
  className?: string
  headerClassName?: string
}) => {
  return (
    <div className={classNames(styles.subsection, className)}>
      <FormSubheader
        className={classNames(headerClassName)}
        required={required}
        help={help}
        onWeb={onWeb}
      >
        {header}
      </FormSubheader>
      {children}
    </div>
  )
}

export const InfoBox = ({
  children,
  className,
  ...rest
}: HTMLAttributes<HTMLDivElement>) => (
  <div className={classNames(styles.infoBox, className)} {...rest}>
    {children}
  </div>
)

export const Label = ({
  children,
  className,
  required,
  ...rest
}: HTMLProps<HTMLLabelElement> & { required?: boolean }) => (
  <label
    {...rest}
    className={classNames(required && styles.required, className)}
  >
    {children}
  </label>
)

export const FullSizeElement = ({ children }: HTMLProps<HTMLDivElement>) => (
  <div className={styles.fullSize}>{children}</div>
)

export const InlineSection = ({ children }: HTMLProps<HTMLDivElement>) => (
  <div className={styles.inline}>{children}</div>
)

export const ColumnSection = ({ children }: HTMLProps<HTMLDivElement>) => (
  <div className={styles.column}>{children}</div>
)

export const Actions = ({ children }: HTMLProps<HTMLElement>) => (
  <nav className={styles.actions}>{children}</nav>
)
