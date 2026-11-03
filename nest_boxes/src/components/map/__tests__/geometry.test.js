import { describe, expect, it } from "vitest"

import {
  bubbleDiameter,
  circlePolygon,
  clusterByDistance,
} from "@/components/map/geometry.js"

const haversine = ([lng1, lat1], [lng2, lat2]) => {
  const radians = degrees => (degrees * Math.PI) / 180
  const a =
    Math.sin(radians(lat2 - lat1) / 2) ** 2 +
    Math.cos(radians(lat1)) *
      Math.cos(radians(lat2)) *
      Math.sin(radians(lng2 - lng1) / 2) ** 2
  return 2 * 6_371_008.8 * Math.asin(Math.sqrt(a))
}

describe("circlePolygon", () => {
  it("draws a closed ring at the radius", () => {
    const center = [17.04, 48.81]
    const [ring] = circlePolygon(center, 30).coordinates
    expect(ring).toHaveLength(49)
    expect(ring[0]).toEqual(ring[48])
    ring.forEach(point => expect(haversine(center, point)).toBeCloseTo(30, 6))
  })
})

describe("clusterByDistance", () => {
  const point = (name, x, y, weight) => ({ name, x, y, weight })

  it("merges points closer than the distance, named by the biggest", () => {
    const clusters = clusterByDistance(
      [
        point("Kostelisko", 30, 0, 142),
        point("Těšický les", 0, 0, 186),
        point("Praha", 500, 0, 96),
      ],
      50,
    )
    expect(clusters).toHaveLength(2)
    const [merged, single] = clusters
    expect(merged.items.map(item => item.name)).toEqual(["Těšický les", "Kostelisko"])
    expect(merged.weight).toBe(328)
    expect(merged.x).toBe(15)
    expect(single.items.map(item => item.name)).toEqual(["Praha"])
  })

  it("keeps points at the distance apart", () => {
    expect(
      clusterByDistance([point("a", 0, 0, 1), point("b", 50, 0, 1)], 50),
    ).toHaveLength(2)
  })
})

describe("bubbleDiameter", () => {
  it("grows with the box count", () => {
    expect(bubbleDiameter(0)).toBe(26)
    expect(bubbleDiameter(100)).toBe(39)
  })
})
