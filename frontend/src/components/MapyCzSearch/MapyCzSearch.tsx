import classNames from 'classnames'
import { useDebouncedState } from 'hooks/debouncedState'
import { MapItem, useMapSuggest } from 'hooks/useMapSuggest'
import { FC } from 'react'
import Select, { components, MenuProps } from 'react-select'

import style from './MapyCzSearch.module.scss'
import selectStyle from '../SelectObject.module.scss'

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
      formatOptionLabel={OptionLabel}
      className={classNames(className, selectStyle.selectObject, {
        [selectStyle.opportunitiesTheme]: colorTheme === 'opportunities',
      })}
      filterOption={() => true}
      components={{ Menu: MenuWithAttribution }}
      noOptionsMessage={() => {
        if (query !== debouncedQuery) {
          return <>Čekám až dopíšeš&hellip;</>
        } else if (query.length < 2) {
          return 'Zadej alespoň 2 znaky'
        } else {
          return 'Nenalezeno'
        }
      }}
      loadingMessage={() => <>Hledám&hellip;</>}
      placeholder={<>Hledej&hellip;</>}
    />
  )
}
