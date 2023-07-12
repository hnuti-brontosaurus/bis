import { api } from 'app/services/bis'
import { Button } from 'components'
import { useForm } from 'react-hook-form'
import { FaSearchLocation } from 'react-icons/fa'

export const OSMSearch = ({
  onSelect,
  className,
  onError = () => undefined,
}: {
  onSelect: (coords: [number, number], name: string) => void
  className?: string
  onError: (error: Error) => void
}) => {
  const searchMethods = useForm<{
    query: string
  }>()
  const { register, handleSubmit, formState, reset } = searchMethods

  const [searchOSMLocation, { isLoading: isSearching }] =
    api.endpoints.searchLocationOSM.useLazyQuery()

  const handleSearchFormSubmit = handleSubmit(async data => {
    if (data.query.length > 2) {
      try {
        const foundLocations = await searchOSMLocation(data.query).unwrap()

        if (foundLocations.length === 0) {
          throw new Error('Místo nenalezeno')
        }

        onSelect(
          [foundLocations[0].lat, foundLocations[0].lon],
          foundLocations[0].display_name,
        )
        //setFlyBounds(foundLocations[0].boundingbox as L.LatLngBoundsLiteral)
        reset({ query: '' })
      } catch (error) {
        onError(error as Error)
      }
    }
  })

  return (
    <form
      className={className}
      id="osm-place-query"
      onSubmit={handleSearchFormSubmit}
    >
      <fieldset disabled={formState.isSubmitting || isSearching}>
        <input
          form="osm-place-query"
          type="text"
          placeholder="Najít na mapě (OpenStreetMap)"
          {...register('query')}
        />
        <Button secondary type="submit" form="osm-place-query">
          <FaSearchLocation />
        </Button>
      </fieldset>
    </form>
  )
}
