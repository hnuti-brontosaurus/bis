import { FC } from 'react'
import { useDebouncedState } from 'hooks/debouncedState'
import { useMapSuggest } from 'hooks/useMapSuggest'
import { useFormContext } from 'react-hook-form'
import { FormInputError } from '../FormInputError/FormInputError'
import { InlineSection, Label } from '../FormLayout/FormLayout'

interface Props {
  name: string
}

export const AddressSubform: FC<Props> = ({ name }) => {
  const { register } = useFormContext()
  const [query, debouncedQuery, setQuery] = useDebouncedState(250, '')
  const [options, { loading }] = useMapSuggest(debouncedQuery)

  return (
    <>
      <InlineSection>
        <Label>Ulice a číslo domu</Label>
        <FormInputError>
          <input type="text" {...register(`${name}.street`)} />
        </FormInputError>
      </InlineSection>
      <InlineSection>
        <Label>Město</Label>
        <FormInputError>
          <input type="text" {...register(`${name}.city`)} />
        </FormInputError>
      </InlineSection>
      <InlineSection>
        <Label>Směrovačí číslo</Label>
        <FormInputError>
          <input type="text" {...register(`${name}.zip_code`)} />
        </FormInputError>
      </InlineSection>
    </>
  )
}
