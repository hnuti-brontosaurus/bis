<script setup>
import { inject, onBeforeUnmount, watchEffect } from "vue"
import { Marker } from "maplibre-gl"

import { bubbleDiameter } from "@/components/map/geometry.js"
import { areaBubbleElement } from "@/components/map/markers.js"

const OVERLAY = "nest_boxes_regions"

const props = defineProps({
  // PublicRegion[], see data/public.js
  regions: { type: Array, required: true },
})

const { map, setOverlay, removeOverlay } = inject("map")
let markers = []

const clear = () => {
  markers.forEach(marker => marker.remove())
  markers = []
}

watchEffect(() => {
  const features = props.regions.map(region => ({
    type: "Feature",
    properties: { id: region.id },
    geometry: region.outline,
  }))
  setOverlay(OVERLAY, colors => ({
    sources: {
      [OVERLAY]: { type: "geojson", data: { type: "FeatureCollection", features } },
    },
    layers: [
      {
        id: `${OVERLAY}_line`,
        type: "line",
        source: OVERLAY,
        paint: { "line-color": colors.primary, "line-width": 1, "line-opacity": 0.45 },
      },
    ],
  }))
  clear()
  markers = props.regions
    .filter(region => region.box_count)
    .map(region => {
      const element = areaBubbleElement({
        plain: true,
        count: region.box_count,
        done: 0,
        attention: 0,
        diameter: bubbleDiameter(region.box_count),
        name: region.name,
      })
      return new Marker({ element, anchor: "center" })
        .setLngLat(region.marker.coordinates)
        .addTo(map.value)
    })
})

onBeforeUnmount(() => {
  clear()
  removeOverlay(OVERLAY)
})
</script>

<template>
  <span hidden />
</template>
