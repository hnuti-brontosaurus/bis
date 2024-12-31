import { useDebouncedState } from 'hooks/debouncedState'
import { useEffect, useState } from 'react'

const API_KEY = process.env.REACT_APP_MAPY_CZ_API_KEY

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
  const [options, setOptions] = useState([])
  useEffect(() => {
    if (query.length >= 2) {
      fetch(
        `https://api.mapy.cz/v1/suggest?query=${debouncedQuery}&apikey=${API_KEY}`,
      )
        .then(result => result.json())
        .then(options => setOptions(options.items))
    }
  }, [debouncedQuery, setOptions])

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
