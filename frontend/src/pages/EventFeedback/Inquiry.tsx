import { InquiryRead, InquiryType } from 'app/services/bisTypes'
import classNames from 'classnames'
import {
  Button,
  ExternalButtonLink,
  FormInputError,
  FormSubsection,
} from 'components'
import { sanitize } from 'dompurify'
import range from 'lodash/range'
import {
  createContext,
  FC,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import { useFormContext } from 'react-hook-form'
import { HiExternalLink } from 'react-icons/hi'
import { required } from 'utils/validationMessages'
import styles from './Inquiry.module.scss'

interface InquiryProps {
  inquiry: InquiryRead
  index: number
}

const InquiryContext = createContext<InquiryProps | null>(null)

const useInquiryContext = (): InquiryProps => {
  const value = useContext(InquiryContext)
  if (!value) {
    throw new Error('Using inquiry context outside of inquiry!')
  }
  return value
}

const useRegister = () => {
  const { inquiry, index } = useInquiryContext()
  const { register } = useFormContext()
  return register(`replies.${index}.reply`, {
    required: inquiry.is_required && required,
  })
}

const TextInquiry: FC = () => {
  const register = useRegister()
  return <textarea className={styles.text} {...register} />
}

const OptionInquiry: FC = () => {
  const { inquiry } = useInquiryContext()
  const register = useRegister()
  return (
    <fieldset
      className={classNames(styles.wrap, styles.options, {
        [styles.horizontalLayout]: inquiry.data?.layout === 'horizontal',
      })}
    >
      {inquiry.data?.options?.map(({ option, href }) => (
        <label
          key={option}
          className={classNames(styles.wrap, `${inquiry.data!.type}Label`)}
        >
          <input type={inquiry.data!.type} value={option} {...register} />
          <span>
            {option}
            {href && (
              <ExternalButtonLink
                target="__blank"
                rel="noopener noreferrer"
                tertiary
                href={href}
                className={styles.optionLink}
              >
                <HiExternalLink />
              </ExternalButtonLink>
            )}
          </span>
        </label>
      ))}
      {inquiry.data?.otherOption && <OtherOption />}
    </fieldset>
  )
}

const OtherOption: FC = () => {
  const { inquiry, index } = useInquiryContext()
  const { register } = useFormContext()
  const registerField = useRegister()

  return (
    <label className={`${inquiry.data!.type}Label`}>
      <input type={inquiry.data!.type} value="jiné" {...registerField} />
      <div className={styles.other}>
        <span>jiné:</span>
        <input type="text" {...register(`replies.${index}.data.other`)} />
      </div>
    </label>
  )
}

const ScaleInquiry: FC = () => {
  const { inquiry, index } = useInquiryContext()
  const { register, getValues } = useFormContext()
  const [showComment, setShowComment] = useState(
    !!getValues(`replies.${index}.data.comment`),
  )

  return (
    <>
      <div className={styles.scale}>
        <div>
          <fieldset className={styles.scaleRange}>
            <div className={styles.scaleLabel}>zcela nesplňuje</div>
            {range(1, 6).map(rating => (
              <label
                key={rating}
                className={classNames('radioLabel', styles.scaleOption)}
              >
                <input
                  type="radio"
                  value={rating}
                  {...register(`replies.${index}.reply`, {
                    required: inquiry.is_required && required,
                  })}
                />
                {rating}
              </label>
            ))}
            <div className={styles.scaleLabel}>zcela splňuje</div>
          </fieldset>
        </div>
        {inquiry.data?.comment && (
          <Button type="button" tertiary onClick={() => setShowComment(true)}>
            přidat komentář
          </Button>
        )}
      </div>
      {showComment && (
        <textarea
          className={classNames(styles.text, styles.scaleText)}
          {...register(`replies.${index}.data.comment`)}
        />
      )}
    </>
  )
}

const components: Record<InquiryType, FC> = {
  text: TextInquiry,
  checkbox: OptionInquiry,
  radio: OptionInquiry,
  scale: ScaleInquiry,
  header: () => null,
}

const InquiryQuestion: FC<{ text: string }> = ({ text }) => {
  const ref = useRef<HTMLSpanElement>(null)
  useEffect(() => {
    ref.current?.querySelectorAll('a')?.forEach(link => {
      link.target = '__blank'
      link.rel = 'noopener noreferrer'
    })
  }, [text])
  return (
    <span
      className={styles.questionText}
      ref={ref}
      dangerouslySetInnerHTML={{ __html: sanitize(text) }}
    />
  )
}

export const Inquiry: FC<InquiryProps> = ({ inquiry, index }) => {
  const { setValue } = useFormContext()
  useEffect(() => {
    setValue(`replies.${index}.inquiry`, inquiry.id)
  }, [setValue, index, inquiry.id])
  const context = useMemo(
    () => ({
      inquiry,
      index,
    }),
    [inquiry, index],
  )

  const type = inquiry.data!.type
  const Component = components[type]

  return (
    <InquiryContext.Provider value={context}>
      <FormSubsection
        header={<InquiryQuestion text={inquiry.inquiry} />}
        required={inquiry.is_required}
        className={styles.question}
        headerClassName={styles.wrap}
      >
        <FormInputError name={`replies.${index}.reply`} isBlock>
          <div className={styles.answer}>
            <Component />
          </div>
        </FormInputError>
      </FormSubsection>
    </InquiryContext.Provider>
  )
}
