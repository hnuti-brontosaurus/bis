import { onBeforeUnmount, shallowRef } from "vue"

/** The phone's position as a GeoJSON point with `accuracy` in metres, null until known. */
export const usePosition = () => {
  const position = shallowRef(null)
  const watcher = navigator.geolocation.watchPosition(
    ({ coords }) => {
      position.value = {
        type: "Point",
        coordinates: [coords.longitude, coords.latitude],
        accuracy: coords.accuracy,
      }
    },
    () => {},
    { enableHighAccuracy: true },
  )
  onBeforeUnmount(() => navigator.geolocation.clearWatch(watcher))
  return position
}
