import { useSMap } from 'hooks/useSMap'
import { useEffect, useRef } from 'react'

export const MapyCzSearch = ({
  onSelect,
  className,
}: {
  onSelect: (coords: [number, number], name: string) => void
  className?: string
  // unused prop to ensure that the component has the same interface as OSMSearch
  onError: (error: Error) => void
}) => {
  const inputRef = useRef<HTMLInputElement>(null)
  const [SMap] = useSMap()

  useEffect(() => {
    if (SMap && inputRef.current) {
      const cb = (suggestData: any) => {
        inputRef.current!.value = ''
        onSelect(
          [suggestData.data.latitude, suggestData.data.longitude],
          suggestData.phrase,
        )
      }
      const suggest = new SMap.Suggest(inputRef.current)
      suggest.addListener('suggest', cb)

      return () => {
        suggest.removeListener('suggest', cb)
        suggest.destroy()
      }
    }
  }, [SMap, onSelect])

  return (
    <input
      className={className}
      type="text"
      ref={inputRef}
      placeholder="Hledej místo na mapě"
    />
  )
}
