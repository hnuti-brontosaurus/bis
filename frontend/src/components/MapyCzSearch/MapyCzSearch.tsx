import { useDebouncedState } from 'hooks/debouncedState'
import { MapItem, useMapSuggest } from 'hooks/useMapSuggest'
import { useState } from 'react'
import Select from 'react-select'

export const MapyCzSearch = ({
  onSelect,
  className,
}: {
  onSelect: (coords: [number, number], name: string) => void
  className?: string
  // unused prop to ensure that the component has the same interface as OSMSearch
  onError: (error: Error) => void
}) => {
  const [value, setValueInternal] = useState<MapItem | null>(null)
  const [query, debouncedQuery, setQuery] = useDebouncedState(1000, '')
  const options = useMapSuggest(debouncedQuery)

  const setValue = (newValue: MapItem | null) => {
    setValueInternal(newValue)
    if (newValue) {
      onSelect([newValue.position.lat, newValue.position.lon], newValue.name)
    }
  }

  return (
    <Select<MapItem>
      options={options}
      inputValue={query}
      onInputChange={setQuery}
      value={value}
      onChange={setValue}
      getOptionLabel={option => option.name}
      className={className}
    />
  )
}
