import { InquiryRead } from 'app/services/bisTypes'
import { FormInputError, FormSubsection } from 'components'
import { createContext, FC, useContext, useEffect, useMemo } from 'react'
import { useFormContext } from 'react-hook-form'
import { required } from 'utils/validationMessages'

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
  return <textarea {...register} />
}

const OptionInquiry: FC = () => {
  const { inquiry } = useInquiryContext()
  const register = useRegister()
  return (
    <fieldset>
      {inquiry.data?.options?.map(({ option }) => (
        <label key={option}>
          <input type={inquiry.data!.type} value={option} {...register} />
          {option}
        </label>
      ))}
    </fieldset>
  )
}

const components: { [key: string]: FC } = {
  text: TextInquiry,
  checkbox: OptionInquiry,
  radio: OptionInquiry,
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
  if (!Component) {
    throw new Error(`Unsupported inquiry type "${type}"!`)
  }

  return (
    <InquiryContext.Provider value={context}>
      <FormSubsection header={inquiry.inquiry} required={inquiry.is_required}>
        <FormInputError name={`replies.${index}.reply`}>
          <Component />
        </FormInputError>
      </FormSubsection>
    </InquiryContext.Provider>
  )
}
