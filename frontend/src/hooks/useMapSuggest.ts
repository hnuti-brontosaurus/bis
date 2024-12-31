import { useEffect, useState } from 'react'
interface ApiResponse {
  items: MapItem[]
}
export interface MapItem {
  name: string
  label: string
  position: { lon: number; lat: number }
}

export const useMapSuggest = (query: string): MapItem[] => {
  const [results, setResults] = useState([] as MapItem[])

  useEffect(() => {
    const params = new URLSearchParams({
      query,
    })
    fetch(`https://api.mapy.cz/v1/suggest?${params.toString()}`, {
      headers: {
        'X-Mapy-Api-Key': process.env.REACT_APP_MAPY_CZ_API_KEY,
      } as HeadersInit,
    })
      .then(response => response.json())
      .then((response: ApiResponse) => setResults(response.items))
  }, [query, setResults])

  return results
}
