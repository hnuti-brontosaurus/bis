import { useDebouncedState } from 'hooks/debouncedState'
import { MapItem, useMapSuggest } from 'hooks/useMapSuggest'
import { FC } from 'react'
import { Controller, useFormContext } from 'react-hook-form'
import Select, { FormatOptionLabelMeta } from 'react-select'
import { FormInputError } from '../FormInputError/FormInputError'
import { InlineSection, Label } from '../FormLayout/FormLayout'

interface Props {
  name: string
}

const OptionLabel = (
  { name, location }: MapItem,
  { context }: FormatOptionLabelMeta<MapItem>,
) => (
  <div>
    <div>{name}</div>
    {context === 'menu' && (
      <div style={{ color: 'gray', fontSize: '.7em' }}>{location}</div>
    )}
  </div>
)

export const AddressSubform: FC<Props> = ({ name }) => {
  const { register, setValue } = useFormContext()
  const [query, debouncedQuery, setQuery] = useDebouncedState(250, '')
  const [options, { loading }] = useMapSuggest(debouncedQuery, {
    locationType: ['regional.address'],
  })

  return (
    <>
      <InlineSection>
        <Label>Ulice a číslo domu</Label>
        <FormInputError>
          <Controller
            name={`${name}.street`}
            render={({ field: { name: inputName, onChange, value, ref } }) => (
              <Select<MapItem>
                name={inputName}
                inputValue={query}
                onInputChange={setQuery}
                onChange={(newValue: MapItem | null) => {
                  if (newValue) {
                    onChange(newValue.name)
                    const city = newValue.regionalStructure.find(
                      ({ type }) => type === 'regional.municipality',
                    )
                    setValue(name, {
                      city: city?.name,
                      zip_code: newValue.zip,
                    })
                  } else {
                    onChange('')
                  }
                }}
                options={options}
                filterOption={() => true}
                getOptionValue={({ name }) => name}
                formatOptionLabel={OptionLabel}
              />
            )}
          />
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
