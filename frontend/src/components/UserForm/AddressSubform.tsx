import classNames from 'classnames'
import { useDebouncedState } from 'hooks/debouncedState'
import { MapItem, useMapSuggest } from 'hooks/useMapSuggest'
import { FC } from 'react'
import { Controller, useFormContext } from 'react-hook-form'
import Select from 'react-select'
import { FormInputError } from '../FormInputError/FormInputError'
import { InlineSection, Label } from '../FormLayout/FormLayout'
import {
  createOptionLabel,
  loadingMessage,
  MenuWithAttribution,
  noOptionsMessage,
} from '../MapyCzSearch/MapyCzComponents'

import style from './AddressSubform.module.scss'
import selectStyle from '../SelectObject.module.scss'

interface Props {
  name: string
  colorTheme?: string
}

type Option = Pick<MapItem, 'name' | 'regionalStructure'> &
  Partial<Pick<MapItem, 'location' | 'zip'>>

const sameName = (name: string) => (option: Option) => name === option.name

const createOption = (name: string): Option => ({ name, regionalStructure: [] })

export const AddressSubform: FC<Props> = ({ name, colorTheme }) => {
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
            render={({ field: { name: inputName, onChange, value, ref } }) => {
              const finalOptions =
                options.find(sameName(value)) && value !== ''
                  ? options
                  : (options as Option[]).concat([createOption(value)]) // create option for initial field value
              return (
                <Select<Option>
                  ref={ref}
                  name={inputName}
                  className={classNames(
                    selectStyle.selectObject,
                    style.select,
                    {
                      [selectStyle.opportunitiesTheme]:
                        colorTheme === 'opportunuties',
                    },
                  )}
                  value={finalOptions.find(sameName(value))}
                  inputValue={query}
                  onInputChange={setQuery}
                  onChange={(newValue: Option | null) => {
                    if (newValue) {
                      const city = newValue.regionalStructure.find(
                        ({ type }) => type === 'regional.municipality',
                      )
                      setValue(`${name}.city`, city?.name)
                      setValue(`${name}.zip_code`, newValue.zip)
                      onChange(newValue.name)
                    } else {
                      onChange('')
                    }
                  }}
                  options={finalOptions}
                  filterOption={
                    option => !!options.find(sameName(option.value)) // hide initial value option
                  }
                  getOptionValue={({ name }) => name}
                  formatOptionLabel={createOptionLabel(
                    ({ name }) => name,
                    ({ location }) => location,
                  )}
                  isLoading={loading}
                  components={{ Menu: MenuWithAttribution }}
                  loadingMessage={loadingMessage}
                  noOptionsMessage={noOptionsMessage(query, debouncedQuery, 2)}
                />
              )
            }}
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
