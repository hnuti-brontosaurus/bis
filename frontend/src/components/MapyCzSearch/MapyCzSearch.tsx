import classNames from 'classnames'
import { useDebouncedState } from 'hooks/debouncedState'
import { MapItem, useMapSuggest } from 'hooks/useMapSuggest'
import Select from 'react-select'
import {
  createOptionLabel,
  loadingMessage,
  MenuWithAttribution,
  noOptionsMessage,
} from './MapyCzComponents'

import selectStyle from '../SelectObject.module.scss'

export const MapyCzSearch = ({
  onSelect,
  className,
  colorTheme,
}: {
  onSelect: (coords: [number, number], name: string) => void
  className?: string
  // unused prop to ensure that the component has the same interface as OSMSearch
  onError: (error: Error) => void
  colorTheme?: string
}) => {
  const [query, debouncedQuery, setQuery] = useDebouncedState(250, '')
  const [options, { loading }] = useMapSuggest(debouncedQuery, {
    minQueryLength: 2,
  })

  const setValue = (newValue: MapItem | null) => {
    if (newValue) {
      onSelect([newValue.position.lat, newValue.position.lon], newValue.name)
    }
  }

  return (
    <Select<MapItem>
      options={options}
      inputValue={query}
      onInputChange={setQuery}
      value={null}
      isLoading={loading}
      onChange={setValue}
      getOptionValue={({ name }) => name}
      formatOptionLabel={createOptionLabel(
        ({ name }) => name,
        ({ label, location }) => `${label}, ${location}`,
      )}
      className={classNames(className, selectStyle.selectObject, {
        [selectStyle.opportunitiesTheme]: colorTheme === 'opportunities',
      })}
      filterOption={() => true}
      components={{ Menu: MenuWithAttribution }}
      noOptionsMessage={noOptionsMessage(query, debouncedQuery, 2)}
      loadingMessage={loadingMessage}
      placeholder={<>Hledej&hellip;</>}
    />
  )
}
