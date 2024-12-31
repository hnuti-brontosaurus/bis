import { useDebouncedState } from 'hooks/debouncedState'
import { MapItem, useMapSuggest } from 'hooks/useMapSuggest'
import { FC } from 'react'
import Select, { components, MenuProps } from 'react-select'

import style from './MapyCzSearch.module.scss'

const OptionLabel: FC<MapItem> = ({ name, label, location }) => (
  <div>
    <div>{name}</div>
    <div className={style.specific}>
      {label}, {location}
    </div>
  </div>
)

const MenuWithAttribution: FC<MenuProps<MapItem>> = props => (
  <components.Menu {...props}>
    {props.children}
    <div className={style.attribution}>
      Hledají <img src="https://api.mapy.cz/img/api/logo-small.svg" />
    </div>
  </components.Menu>
)

export const MapyCzSearch = ({
  onSelect,
  className,
}: {
  onSelect: (coords: [number, number], name: string) => void
  className?: string
  // unused prop to ensure that the component has the same interface as OSMSearch
  onError: (error: Error) => void
}) => {
  const [query, debouncedQuery, setQuery] = useDebouncedState(1000, '')
  const options = useMapSuggest(debouncedQuery)

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
      onChange={setValue}
      getOptionValue={({ name }) => name}
      formatOptionLabel={OptionLabel}
      className={className}
      components={{ Menu: MenuWithAttribution }}
    />
  )
}
