<script setup>
import { inject, onBeforeUnmount, watchEffect } from "vue"
import { Marker } from "maplibre-gl"

import { bubbleDiameter } from "@/components/map/geometry.js"
import { areaBubbleElement } from "@/components/map/markers.js"

const props = defineProps({
  // PublicRegion[], see data/public.js
  regions: { type: Array, required: true },
})

const { map } = inject("map")
let markers = []

const clear = () => {
  markers.forEach(marker => marker.remove())
  markers = []
}

watchEffect(() => {
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

onBeforeUnmount(clear)
</script>

<template>
  <span hidden />
</template>
