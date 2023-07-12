import classNames from 'classnames'
import { Button } from 'components'
import { useSearchParamsState } from 'hooks/searchParamsState'
import { useSwipe } from 'hooks/useSwipe'
import { Children, FC, FunctionComponentElement, ReactNode } from 'react'
import { FaArrowCircleLeft, FaArrowCircleRight } from 'react-icons/fa'
import styles from './Steps.module.scss'

export const Steps = <T extends Record<string, any>>({
  children,
  actions,
  onSubmit,
  onCancel,
}: {
  onSubmit?: (props: T) => void
  onCancel?: () => void
  actions?: { name: string; props: T }[]
  children:
    | FunctionComponentElement<{
        name: string
        hasError?: boolean
        hidden?: boolean
      }>
    | FunctionComponentElement<{
        name: string
        hasError?: boolean
        hidden?: boolean
      }>[]
}) => {
  const [step, setStep] = useSearchParamsState('krok', 1, i => Number(i))
  const elementProps = Children.map(children, element => ({
    name: element.props.name,
    hasError: element.props.hasError ?? false,
    hidden: element.props.hidden,
  })).filter(element => !element.hidden)

  const nextStep = () => {
    setStep(Math.min(step + 1, elementProps.length))
  }
  const prevStep = () => {
    setStep(Math.max(step - 1, 1))
  }
  const swipeRef = useSwipe(
    direction => {
      if (direction === 'left') {
        nextStep()
      }
      if (direction === 'right') {
        prevStep()
      }
    },
    { ignoredClass: 'steps-change-swipe-ignored' },
  )
  return (
    <div ref={swipeRef}>
      <div className={styles.navWrapper}>
        <nav className={styles.navigation}>
          {elementProps.map(({ name, hasError }, i) => (
            <button
              type="button"
              className={classNames(
                i + 1 === step && styles.isActive,
                styles.stepButton,
                hasError && styles.isError,
              )}
              key={name}
              onClick={() => setStep(i + 1)}
            >
              {name}
            </button>
          ))}
        </nav>
        <nav className={classNames(styles.actions, styles.topActions)}>
          {onCancel && (
            <Button
              secondary
              type="reset"
              onClick={() => onCancel()}
              className={styles.topActionsButton}
            >
              Zrušit
            </Button>
          )}
          {onSubmit &&
            actions &&
            actions.map(({ props, name }) => (
              <Button
                key={name}
                primary
                type="submit"
                onClick={() => onSubmit(props)}
                className={styles.topActionsButton}
              >
                {name}
              </Button>
            ))}
        </nav>
      </div>
      {Children.map(children, element => element)
        .filter(element => !element.props.hidden)
        .map((element, i) => (
          <div
            key={element.props.name}
            className={classNames(i !== step - 1 && styles.isHidden)}
          >
            {element}
          </div>
        ))}
      {step > 1 && (
        <Button
          tertiary
          type="button"
          aria-label="Go to previous step"
          onClick={() => {
            prevStep()
            window.scrollTo(0, 0)
          }}
          className={styles.buttonNavigationLeftBigScreen}
        >
          <FaArrowCircleLeft className={styles.floatingStepArrow} />
        </Button>
      )}
      {step < elementProps.length && (
        <Button
          tertiary
          type="button"
          aria-label="Go to next step"
          onClick={() => {
            nextStep()
            window.scrollTo(0, 0)
          }}
          className={styles.buttonNavigationRightBigScreen}
        >
          <FaArrowCircleRight className={styles.floatingStepArrow} />
        </Button>
      )}
      <nav className={styles.bottomNavigation}>
        {step > 1 && (
          <Button
            tertiary
            type="button"
            aria-label="Go to previous step"
            onClick={() => {
              prevStep()
              window.scrollTo(0, 0)
            }}
          >
            <FaArrowCircleLeft className={styles.floatingStepArrow} />
          </Button>
        )}
        <span className={styles.spacer}></span>
        {step < elementProps.length && (
          <Button
            tertiary
            type="button"
            aria-label="Go to next step"
            onClick={() => {
              nextStep()
              window.scrollTo(0, 0)
            }}
          >
            <FaArrowCircleRight className={styles.floatingStepArrow} />
          </Button>
        )}
      </nav>
      <nav className={styles.actions}>
        {onCancel && (
          <Button secondary type="reset" onClick={() => onCancel()}>
            Zrušit
          </Button>
        )}
        {onSubmit &&
          actions &&
          actions.map(({ props, name }) => (
            <Button
              key={name}
              primary
              type="submit"
              onClick={() => onSubmit(props)}
            >
              {name}
            </Button>
          ))}
      </nav>
    </div>
  )
}

export const Step: FC<{
  name: string
  hasError?: boolean
  fields?: string[]
  children?: ReactNode
  hidden?: boolean
}> = ({ children }) => <>{children}</>
