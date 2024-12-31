import { useDebouncedState } from 'hooks/debouncedState'
import { useMapSuggest } from 'hooks/useMapSuggest'

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

  return (
    <>
      <input
        className={className}
        type="text"
        value={query}
        onChange={event => setQuery(event.target.value)}
        placeholder="Hledej místo na mapě"
      />
      <ul>
        {options.map(option => (
          <li key={option.name}>{option.name}</li>
        ))}
      </ul>
    </>
  )
}
