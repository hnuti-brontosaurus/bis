import { useEffect, useState } from 'react'
interface ApiResponse {
  items: MapItem[]
}
export interface MapItem {
  name: string
  label: string
  position: { lon: number; lat: number }
  location: string
}

interface Props {
  minQueryLength?: number
}

export const useMapSuggest = (
  query: string,
  { minQueryLength = 2 }: Props = {},
): [MapItem[], { loading: boolean }] => {
  const [results, setResults] = useState<MapItem[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const params = new URLSearchParams({
      query,
    })
    if (query.length >= minQueryLength) {
      setLoading(true)
      fetch(`https://api.mapy.cz/v1/suggest?${params.toString()}`, {
        headers: {
          'X-Mapy-Api-Key': process.env.REACT_APP_MAPY_CZ_API_KEY,
        } as HeadersInit,
      })
        .then(response => response.json())
        .then((response: ApiResponse) => {
          setResults(response.items)
          setLoading(false)
        })
    } else {
      setResults([])
      setLoading(false)
    }
  }, [query, setResults])

  return [results, { loading }]
}
