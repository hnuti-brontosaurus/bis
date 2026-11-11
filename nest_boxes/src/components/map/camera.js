// Per tab, so that coming back to a map, by the back button or a link, finds
// it as it was left; a new tab starts from the map's own bounds.
const key = name => `map-camera:${name}`

export const rememberCamera = (name, map) => {
  const { lng, lat } = map.getCenter()
  try {
    sessionStorage.setItem(
      key(name),
      JSON.stringify({ center: [lng, lat], zoom: map.getZoom() }),
    )
  } catch {
    // Storage blocked: the map opens at its bounds next time
  }
}

/** { center, zoom } as the map was left, or null. */
export const recallCamera = name => {
  try {
    return JSON.parse(sessionStorage.getItem(key(name)))
  } catch {
    return null
  }
}
