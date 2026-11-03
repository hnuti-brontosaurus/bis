<script setup>
import { inject, onBeforeUnmount, watchEffect } from "vue"
import { Marker } from "maplibre-gl"

import { circlePolygon } from "@/components/map/geometry.js"
import { planLabelElement } from "@/components/map/markers.js"

const props = defineProps({
  // [{ id, name, location: GeoJSON Point, planned_radius: metres }]
  boxes: { type: Array, required: true },
})

const OVERLAY = "nest_boxes_planned"

const { map, setOverlay, removeOverlay } = inject("map")
let labels = []

const clear = () => {
  labels.forEach(label => label.remove())
  labels = []
}

watchEffect(() => {
  const features = props.boxes.map(box => ({
    type: "Feature",
    properties: { id: box.id },
    geometry: circlePolygon(box.location.coordinates, box.planned_radius),
  }))
  setOverlay(OVERLAY, colors => ({
    sources: {
      [OVERLAY]: { type: "geojson", data: { type: "FeatureCollection", features } },
    },
    layers: [
      {
        id: `${OVERLAY}_fill`,
        type: "fill",
        source: OVERLAY,
        paint: { "fill-color": colors.planBg },
      },
      {
        id: `${OVERLAY}_line`,
        type: "line",
        source: OVERLAY,
        paint: {
          "line-color": colors.primary,
          "line-width": 2.5,
          "line-dasharray": [2, 1.5],
        },
      },
    ],
  }))
  clear()
  labels = props.boxes.map(box =>
    new Marker({ element: planLabelElement(box.name), anchor: "center" })
      .setLngLat(box.location.coordinates)
      .addTo(map.value),
  )
})

onBeforeUnmount(() => {
  clear()
  removeOverlay(OVERLAY)
})
</script>

<template>
  <span hidden />
</template>
