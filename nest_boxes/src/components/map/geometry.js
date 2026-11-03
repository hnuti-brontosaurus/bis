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
 * Greedy merge of screen points closer than `distance` px, biggest first, so
 * the biggest item names the group. Each cluster sits at its items' centroid.
 */
export const clusterByDistance = (items, distance) => {
  const clusters = []
  for (const item of [...items].sort((a, b) => b.weight - a.weight)) {
    const near = clusters.find(
      cluster => Math.hypot(cluster.x - item.x, cluster.y - item.y) < distance,
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
