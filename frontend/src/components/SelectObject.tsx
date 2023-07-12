import { ApiEndpointQuery } from '@reduxjs/toolkit/dist/query/core/module'
import { QueryHooks } from '@reduxjs/toolkit/dist/query/react/buildHooks'
import {
  EndpointDefinitions,
  QueryDefinition,
  skipToken,
} from '@reduxjs/toolkit/query'
import type { PaginatedList } from 'app/services/bisTypes'
import { useDebouncedState } from 'hooks/debouncedState'
import { forwardRef, InputHTMLAttributes } from 'react'
import Select from 'react-select'
import { Assign } from 'utility-types'
import styles from './SelectObject.module.scss'

// Redeclare forwardRef - to be able to forward refs to generic components
// https://fettblog.eu/typescript-react-generic-forward-refs/#option-3%3A-augment-forwardref
// but actually, redeclaration was messing with other forwardRef usages, so we just typecast the one that is here
type GenericForwardRef = <T, P = {}>(
  render: (props: P, ref: React.Ref<T>) => React.ReactElement | null,
) => (props: P & React.RefAttributes<T>) => React.ReactElement | null

type SelectObjectProps<T> = Omit<
  Assign<
    InputHTMLAttributes<HTMLInputElement>,
    {
      value?: T
      onChange: (value: T | null) => void
      getDisabled?: (value: T) => string
      getLabel: (value: T) => string
      getValue: (value: T) => string
      colorTheme?: string
    }
  >,
  'defaultValue'
>

type QMany<T> = QueryDefinition<
  { search?: string },
  any,
  any,
  PaginatedList<T>,
  any
>

type QueryReturning<T> = ApiEndpointQuery<QMany<T>, EndpointDefinitions> &
  QueryHooks<QMany<T>>

const SelectObjectInner = <T,>(
  {
    value,
    onChange,
    getDisabled,
    getLabel,
    getValue,
    search,
    className,
    colorTheme,
    ...rest
  }: SelectObjectProps<T> & {
    search: QueryReturning<T>
  },
  ref: React.Ref<any>,
) => {
  const [searchQuery, debouncedSearchQuery, setSearchQuery] = useDebouncedState(
    1000,
    '',
  )
  const { data: options, isLoading: isOptionsLoading } = search.useQuery(
    debouncedSearchQuery.length >= 2
      ? { search: debouncedSearchQuery }
      : skipToken,
  )

  return (
    <Select<T>
      {...rest}
      isLoading={isOptionsLoading}
      ref={ref}
      isClearable
      options={options ? options.results : []}
      inputValue={searchQuery}
      onInputChange={input => setSearchQuery(input)}
      value={value}
      onChange={onChange}
      isOptionDisabled={obj => Boolean(getDisabled?.(obj))}
      getOptionLabel={getLabel}
      getOptionValue={getValue}
      className={`${className} customInput ${styles.selectObject} ${
        colorTheme === 'opportunities' ? `${styles.opportunitiesTheme}` : ''
      }`}
      noOptionsMessage={() => {
        if (!searchQuery || searchQuery.length < 3)
          return <div>Zadej alespoň 2 znaky</div>
        return <div>Nenalezeno</div>
      }}
    />
  )
}

export const SelectObject = (forwardRef as GenericForwardRef)(SelectObjectInner)
