const EARTH_RADIUS = 6_371_008.8

/** A GeoJSON polygon approximating a circle of `radius` metres around [lng, lat]. */
export const circlePolygon = ([lng, lat], radius, steps = 48) => {
  const angular = radius / EARTH_RADIUS
  const latitude = (lat * Math.PI) / 180
  const longitude = (lng * Math.PI) / 180
  const ring = Array.from({ length: steps + 1 }, (_, index) => {
    const bearing = ((index % steps) / steps) * 2 * Math.PI
    const pointLatitude = Math.asin(
      Math.sin(latitude) * Math.cos(angular) +
        Math.cos(latitude) * Math.sin(angular) * Math.cos(bearing),
    )
    const pointLongitude =
      longitude +
      Math.atan2(
        Math.sin(bearing) * Math.sin(angular) * Math.cos(latitude),
        Math.cos(angular) - Math.sin(latitude) * Math.sin(pointLatitude),
      )
    return [(pointLongitude * 180) / Math.PI, (pointLatitude * 180) / Math.PI]
  })
  return { type: "Polygon", coordinates: [ring] }
}

/**
 * Greedy merge of bubbles whose edges are closer than `gap` px, biggest first,
 * so the biggest item names the group. Each cluster sits at its items'
 * centroid. Edges rather than centres, because a big bubble covers the label
 * of a small one next to it.
 */
export const clusterByDistance = (items, gap) => {
  const clusters = []
  for (const item of [...items].sort((a, b) => b.weight - a.weight)) {
    const near = clusters.find(
      cluster =>
        Math.hypot(cluster.x - item.x, cluster.y - item.y) <
        gap + (bubbleDiameter(cluster.weight) + bubbleDiameter(item.weight)) / 2,
    )
    if (near) {
      near.items.push(item)
      near.x += (item.x - near.x) / near.items.length
      near.y += (item.y - near.y) / near.items.length
      near.weight += item.weight
    } else {
      clusters.push({ x: item.x, y: item.y, weight: item.weight, items: [item] })
    }
  }
  return clusters
}

export const bubbleDiameter = boxCount => Math.round(26 + Math.sqrt(boxCount) * 1.3)

const LATITUDE_SPAN = 0.0018
const LONGITUDE_SPAN = 0.0028

/** Bounds of a few hundred metres around [lng, lat], for a map of one box. */
export const aroundPoint = ([lng, lat]) => [
  [lng - LONGITUDE_SPAN, lat - LATITUDE_SPAN],
  [lng + LONGITUDE_SPAN, lat + LATITUDE_SPAN],
]

/** Bounds of GeoJSON points, padded so a single point still makes a map. */
export const boundsOf = points => {
  const lngs = points.map(point => point.coordinates[0])
  const lats = points.map(point => point.coordinates[1])
  return [
    [Math.min(...lngs) - LONGITUDE_SPAN / 4, Math.min(...lats) - LATITUDE_SPAN / 4],
    [Math.max(...lngs) + LONGITUDE_SPAN / 4, Math.max(...lats) + LATITUDE_SPAN / 4],
  ]
}

/** Haversine distance in metres between two GeoJSON points. */
export const distance = (from, to) => {
  const [lng1, lat1] = from.coordinates.map(value => (value * Math.PI) / 180)
  const [lng2, lat2] = to.coordinates.map(value => (value * Math.PI) / 180)
  const a =
    Math.sin((lat2 - lat1) / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin((lng2 - lng1) / 2) ** 2
  return 2 * EARTH_RADIUS * Math.asin(Math.sqrt(a))
}
